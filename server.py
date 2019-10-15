import argparse
import logging
from socket import *
from select import select
from threading import Thread

import logs.server_log_config as log_config
from decorators import try_except_wrapper
from descriptors import Port
from jim.codes import *
from jim.classes.request_body import Msg
from jim.functions import *
from server_db import ServerStorage
# from metaclasses import ServerVerifier


class ServerThread(Thread):
    __slots__ = ('func', 'logger')

    def __init__(self, func, logger):
        super().__init__()
        self.func = func
        self.logger = logger
        self.daemon = True

    @try_except_wrapper
    def run(self):
        self.func()


class Server:
    __slots__ = ('bind_addr', '_port', 'logger', 'socket', 'clients', 'users', 'storage', 'commands', 'listener')

    TCP = (AF_INET, SOCK_STREAM)
    TIMEOUT = 5

    port = Port('_port')

    def __init__(self, bind_addr, port):
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        self.bind_addr = bind_addr
        self.port = port
        self.clients = []
        self.users = {}
        self.storage = ServerStorage()
        self.__init_commands()

    def __init_commands(self):
        self.commands = {
            'get_users': self.storage.get_users_online,
            'add_contact': self.storage.add_contact,
            'rem_contact': self.storage.remove_contact,
            'get_contacts': self.storage.get_contacts,
        }

    def start(self, request_count=5):
        self.socket = socket(*self.TCP)
        self.socket.settimeout(0.5)
        self.socket.bind((self.bind_addr, self.port))
        self.logger.info(f'Config server port - {self.port}| Bind address - {self.bind_addr}')

        self.socket.listen(request_count)
        # self.__listen()

        self.listener = ServerThread(self.__listen, self.logger)
        self.listener.start()
        self.__console()

    def __console(self):
        while True:
            msg = input('Enter command:\n')
            if msg.upper() == 'Q':
                break
            if msg[0] == '#':
                msg = msg[1:]

            command, *args = msg.split(' ')
            if command in self.commands:
                res = self.commands[command](*args)
                print(res)

    def __listen(self):
        self.logger.info('Start listen')
        while True:
            try:
                client, addr = self.socket.accept()
            except OSError:
                pass
            except Exception as ex:
                self.logger.error(ex)
            else:
                self.logger.info(f'Connection from {addr}')
                self.clients.append(client)

            i_clients, o_clients = [], []
            try:
                i_clients, o_clients, ex = select(self.clients, self.clients, [], self.TIMEOUT)
            except OSError:
                pass
            except Exception as ex:
                self.logger.error(ex)

            requests = self.__get_requests(i_clients)
            if requests:
                self.__send_responses(requests, o_clients)

    @try_except_wrapper
    def __get_requests(self, i_clients):
        requests = {}
        for client in i_clients:
            try:
                request = get_data(client)
                requests[client] = request

                if request.action == RequestAction.PRESENCE:
                    if request.body in self.users:
                        requests.pop(client)
                        send_data(client, Response(CONFLICT))
                        self.clients.remove(client)
                    else:
                        self.users[request.body] = client
                        self.storage.login_user(request.body, client.getpeername()[0])
                elif request.action == RequestAction.QUIT:
                    self.__client_disconnect(client)
            except (ConnectionError, ValueError):
                self.__client_disconnect(client)
            except Exception as e:
                raise e
        return requests

    @try_except_wrapper
    def __send_responses(self, requests, o_clients):

        for client, i_req in requests.items():
            other_clients = [c for c in o_clients if c != client]
            self.logger.info(client)
            self.logger.info(i_req)

            if i_req.action == RequestAction.PRESENCE:
                self.__send_to_client(client, Response(OK))
                self.__send_to_all(other_clients, Response(BASIC, f'{i_req.body} connected'))
            elif i_req.action == RequestAction.QUIT:
                self.__client_disconnect(client)
            elif i_req.action == RequestAction.MESSAGE:
                msg = Msg.from_dict(i_req.body)
                if msg.to.upper() != 'ALL' and msg.to in self.users:
                    self.__send_to_client(self.users[msg.to], Response(BASIC, str(msg)))
                else:
                    self.__send_to_all(other_clients, Response(BASIC, str(msg)))
            elif i_req.action == RequestAction.COMMAND:
                command, *args = i_req.body.split()
                user = [u for u, c in self.users.items() if c == client].pop()
                args.insert(0, user)
                # o_resp = Response(ANSWER, self.__execute_command(command, *args))
                o_resp = self.__execute_command(command, *args)
                self.__send_to_client(client, o_resp)
            else:
                self.__send_to_client(client, Response(INCORRECT_REQUEST))
                self.logger.error(f'Incorrect request:\n {i_req}')

    @try_except_wrapper
    def __send_to_client(self, client, resp):
        try:
            send_data(client, resp)
        except ConnectionError:
            self.__client_disconnect(client)
        except Exception as e:
            raise e

    def __send_to_all(self, clients, resp):
        for cl in clients:
            self.__send_to_client(cl, resp)

    @try_except_wrapper
    def __client_disconnect(self, client):
        self.clients.remove(client)
        disconnected_user = [u for u, c in self.users.items() if c == client].pop()
        self.users.pop(disconnected_user)
        self.storage.logout_user(disconnected_user)
        disconnection_response = Response(BASIC, f'{disconnected_user} disconnected')
        for cl in self.clients:
            send_data(cl, disconnection_response)

    def __execute_command(self, command, *args):
        if command in self.commands:
            answer = self.commands[command](*args)
            if answer is False:
                return Response(SERVER_ERROR, 'Command error')
            elif isinstance(answer, list):
                answer = [str(a) for a in answer]
                return Response(ANSWER, answer)
            elif answer is None:
                return Response(ANSWER, 'Done')
            return Response(ANSWER, answer)
        else:
            return Response(INCORRECT_REQUEST, 'Command not found')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=7777, type=int, nargs='?', help='Port [default=7777]')
    parser.add_argument('-a', '--addr', default='', type=str, nargs='?', help='Bind address')

    args = parser.parse_args()
    addr = args.addr
    port = args.port

    server = Server(addr, port)
    server.start()


if __name__ == '__main__':
    main()
