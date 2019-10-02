import argparse
from socket import *
from select import select

from decorators import *
from jim.functions import *
import logging
import logs.server_log_config as log_config


class Server:

    __slots__ = ('bind_addr', 'port', 'logger', 'socket', 'clients', 'users')

    TCP = (AF_INET, SOCK_STREAM)
    TIMEOUT = 5

    def __init__(self, bind_addr, port):
        self.bind_addr = bind_addr
        self.port = port
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        self.clients = []
        self.users = {}

    def start(self, request_count=5):
        self.socket = socket(*self.TCP)
        self.socket.settimeout(0.5)
        self.socket.bind((self.bind_addr, self.port))
        self.logger.info(f'Config server port - {self.port}| Bind address - {self.bind_addr}')

        self.socket.listen(request_count)
        self.__listen()

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
                    self.users[request.body] = client
                elif request.action == RequestAction.QUIT:
                    self.users.pop(request.body)

            except ConnectionError:
                self.__client_disconnect(client)
            except Exception as e:
                raise e
        return requests

    @try_except_wrapper
    def __send_responses(self, requests, o_clients):

        for client, i_req in requests.items():
            i_resp = self.__generate_response(i_req)
            self.logger.info(client)
            self.logger.info(i_resp)

            if i_req.action == RequestAction.QUIT:
                self.__client_disconnect(client)
            else:
                self.__send_to_client(client, i_resp)

            if i_req.action == RequestAction.MESSAGE:
                msg = Msg.from_dict(i_req.body)
                if msg.to.lower() == 'server':
                    o_resp = Msg(self.__execute_command(msg.text.strip()), 'server', msg.sender)
                    o_req = Request(RequestAction.MESSAGE, o_resp)
                    self.__send_to_client(self.users[msg.sender], o_req)
                    continue

                if msg.to.upper() != 'ALL' and msg.to in self.users:
                    self.__send_to_client(self.users[msg.to], i_req)
                    continue

            for o_cl in o_clients:
                if client == o_cl:
                    continue
                self.__send_to_client(o_cl, i_req)

    @try_except_wrapper
    def __send_to_client(self, client, req):
        try:
            send_request(client, req)
        except ConnectionError:
            self.__client_disconnect(client)
        except Exception as e:
            raise e

    @try_except_wrapper
    def __generate_response(self, request):
        action = request.action
        body = request.body

        if action == RequestAction.PRESENCE:
            return Response(OK)
        elif action == RequestAction.QUIT:
            return Response(OK)
        elif action == RequestAction.MESSAGE:
            msg = Msg.from_dict(body)
            self.logger.debug(f'Message: {str(msg)}')
            return Response(BASIC)
        return Response(INCORRECT_REQUEST)

    @try_except_wrapper
    def __client_disconnect(self, client):
        self.clients.remove(client)
        disconnected_user = [u for u, c in self.users.items() if c == client].pop()
        self.users.pop(disconnected_user)
        disconnection_request = Request(RequestAction.QUIT, disconnected_user)
        for cl in self.clients:
            send_request(cl, disconnection_request)

    def __execute_command(self, command):
        if command == 'get_users':
            answer = f'Users connected: {", ".join([u for u in self.users.keys()])}'
        else:
            answer = 'Command not found'
        return answer


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
