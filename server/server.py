import logging
from socket import socket, AF_INET, SOCK_STREAM
from select import select
from threading import Thread

import logs.server_log_config as log_config
from common.decorators import try_except_wrapper
from common.descriptors import Port
from jim.classes.package import Response
from jim.codes import ANSWER, AUTH, START_CHAT, ACCEPT_CHAT, \
                      OK, CONNECTED, DISCONNECTED, LETTER, \
                      CONFLICT, UNAUTHORIZED, SERVER_ERROR, INCORRECT_REQUEST
from jim.constants import RequestAction
from jim.classes.request_body import Msg
from jim.functions import send_data, get_data
from server_crypt import gen_keys, decrypt_password, get_hash_password
from server_db import ServerStorage


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
    __slots__ = ('bind_addr', '_port', 'logger', 'socket',
                 'clients', 'users', 'client_keys', 'listener',
                 'storage', 'commands', 'request_handlers')

    TCP = (AF_INET, SOCK_STREAM)
    TIMEOUT = 5

    port = Port('_port')

    def __init__(self, bind_addr, port):
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        self.bind_addr = bind_addr
        self.port = port
        self.clients = []
        self.client_keys = {}
        self.users = {}
        self.storage = ServerStorage()
        self.__init_commands()
        self.__init_req_handlers()

    def __init_commands(self):
        self.commands = {
            'get_users': self.storage.get_users_online,
            'add_contact': self.storage.add_contact,
            'rem_contact': self.storage.remove_contact,
            'get_contacts': self.storage.get_contacts,
            'get_chat': self.storage.get_chat_str
        }

    def __init_req_handlers(self):
        self.request_handlers = {
            RequestAction.PRESENCE: self.__req_presence_handler,
            RequestAction.AUTH: self.__req_auth_handler,
            RequestAction.QUIT: lambda r, c, *a: self.__client_disconnect(c),
            RequestAction.START_CHAT: self.__req_start_chat_handler,
            RequestAction.ACCEPT_CHAT: self.__req_accept_chat_handler,
            RequestAction.MESSAGE: self.__req_message_handler,
            RequestAction.COMMAND: self.__req_command_handler,
        }

    def start(self, request_count=5):
        self.socket = socket(*self.TCP)
        self.socket.settimeout(0.5)
        self.socket.bind((self.bind_addr, self.port))
        start_msg = f'Config server port - {self.port}| ' \
                    f'Bind address - {self.bind_addr}'
        self.logger.info(start_msg)

        self.socket.listen(request_count)
        self.listener = ServerThread(self.__listen, self.logger)
        self.listener.start()

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
                i_clients, o_clients, ex = select(self.clients, self.clients,
                                                  [], self.TIMEOUT)
            except OSError:
                pass
            except Exception as exc:
                self.logger.error(exc)

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
            action = i_req.action
            if action in self.request_handlers:
                self.request_handlers[action](i_req, client, other_clients)
            else:
                self.__send_to_client(client, Response(INCORRECT_REQUEST))
                self.logger.error(f'Incorrect request:\n {i_req}')

    @try_except_wrapper
    def __send_to_client(self, client, resp):
        try:
            self.logger.debug(resp)
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
        user = [u for u, c in self.users.items() if c == client].pop()
        self.users.pop(user)
        self.storage.logout_user(user)
        disconnection_response = Response(DISCONNECTED, user)
        self.logger.debug(disconnection_response)
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

    # region Request handlers

    @try_except_wrapper
    def __req_presence_handler(self, i_req, client, *args):
        prv, pub = gen_keys()
        self.client_keys[i_req.body] = (client, prv)
        self.__send_to_client(client, Response(AUTH,
                                               pub.export_key().decode()))

    @try_except_wrapper
    def __req_auth_handler(self, i_req, client, *args):
        other_clients = args[0]
        user = [u for u, c in self.users.items() if c == client]
        if len(user) == 0:
            self.logger.warning(f'AUTH: user not found')
            return
        user = user[0]
        cl, key = self.client_keys[user]
        if cl != client:
            self.logger.warning('AUTH: connection sockets not equals')
            return
        password = decrypt_password(key, i_req.body)
        if password is None:
            self.logger.warning('AUTH: decrypt error')
            return
        password_hash = get_hash_password(password, user.encode())
        if not self.storage.authorization_user(user, password_hash):
            self.__send_to_client(client, Response(UNAUTHORIZED))
            self.clients.remove(client)
            self.users.pop(user)
            return
        self.storage.login_user(user, client.getpeername()[0])
        self.__send_to_client(client, Response(OK))
        self.__send_to_all(other_clients, Response(CONNECTED, user))

    @try_except_wrapper
    def __req_start_chat_handler(self, i_req, client, *args):
        msg = Msg.from_dict(i_req.body)
        if msg.to not in self.users:
            self.logger.warning(f'{msg.to} not found')
            return
        self.__send_to_client(self.users[msg.to],
                              Response(START_CHAT, str(msg)))

    @try_except_wrapper
    def __req_accept_chat_handler(self, i_req, client, *args):
        msg = Msg.from_dict(i_req.body)
        if msg.to not in self.users:
            self.logger.warning(f'{msg.to} not found')
            return
        self.__send_to_client(self.users[msg.to],
                              Response(ACCEPT_CHAT, str(msg)))

    @try_except_wrapper
    def __req_message_handler(self, i_req, client, *args):
        other_clients = args[0]
        msg = Msg.from_dict(i_req.body)
        self.storage.user_stat_update(msg.sender, ch_sent=1)
        if msg.to.upper() != 'ALL' and msg.to in self.users:
            self.storage.user_stat_update(msg.to, ch_recv=1)
            self.storage.add_message(msg.sender, msg.to, msg.text)
            self.__send_to_client(self.users[msg.to],
                                  Response(LETTER, str(msg)))
        else:
            self.__send_to_all(other_clients, Response(LETTER, str(msg)))
            for u in self.storage.get_users_online():
                if str(u) == msg.sender:
                    continue
                self.storage.user_stat_update(str(u), ch_recv=1)
                self.storage.add_message(msg.sender, str(u), msg.text)

    @try_except_wrapper
    def __req_command_handler(self, i_req, client, *args):
        command, *args = i_req.body.split()
        user = [u for u, c in self.users.items() if c == client].pop()
        if len(args) < 1 or args[0] != user:
            args.insert(0, user)
        o_resp = self.__execute_command(command, *args)
        self.__send_to_client(client, o_resp)

    # endregion
