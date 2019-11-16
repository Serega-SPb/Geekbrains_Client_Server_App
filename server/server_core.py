""" Module implements server logic of chat application """

import logging
from base64 import b64decode, b64encode
from socket import socket, AF_INET, SOCK_STREAM
from select import select
from time import sleep
from threading import Thread

from logs import server_log_config as log_config
from decorators import try_except_wrapper
from descriptors import Port
from jim.classes.package import Response
from jim.codes import ANSWER, AUTH, START_CHAT, ACCEPT_CHAT, FILE_ANSWER, \
                      OK, CONNECTED, DISCONNECTED, LETTER, \
                      CONFLICT, UNAUTHORIZED, SERVER_ERROR, INCORRECT_REQUEST
from jim.constants import RequestAction
from jim.classes.request_body import Msg
from jim.functions import send_data, get_data
from server_crypt import gen_keys, decrypt_password, get_hash_password
from server_db import ServerStorage


class ServerThread(Thread):
    """ Thread class for async execution the function of server """

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
    """ Class implement receive, handle, response to client request """

    __slots__ = ('bind_addr', '_port', 'logger', 'socket', 'blacklist',
                 'clients', 'users', 'client_keys', 'listener',
                 'storage', 'commands', 'request_handlers', 'images')

    TCP = (AF_INET, SOCK_STREAM)
    TIMEOUT = 5

    port = Port('_port')

    def __init__(self, bind_addr, port):
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        self.bind_addr = bind_addr
        self.port = port
        self.clients = []
        self.blacklist = []
        self.client_keys = {}
        self.users = {}
        self.images = {}
        self.storage = ServerStorage()
        self.__init_commands()
        self.__init_req_handlers()

    def __init_commands(self):
        """ Method fills dictionary commands """

        self.commands = {
            'get_users': self.storage.get_users_online,
            'add_contact': self.storage.add_contact,
            'rem_contact': self.storage.remove_contact,
            'get_contacts': self.storage.get_contacts,
            'get_chat': self.storage.get_chat_str,
            'check_avatar': self.storage.check_avatar_hash
        }

    def __init_req_handlers(self):
        """ Method fills dictionary request handlers """

        self.request_handlers = {
            RequestAction.PRESENCE: self.__req_presence_handler,
            RequestAction.AUTH: self.__req_auth_handler,
            RequestAction.QUIT: lambda r, c, *a: self.__client_disconnect(c),
            RequestAction.START_CHAT: self.__req_start_chat_handler,
            RequestAction.ACCEPT_CHAT: self.__req_accept_chat_handler,
            RequestAction.MESSAGE: self.__req_message_handler,
            RequestAction.COMMAND: self.__req_command_handler,
            RequestAction.IMAGE: self.__req_recv_image_handler,
            RequestAction.END_IMAGE: self.__req_end_recv_image_handler,
            RequestAction.GET_IMAGE: self.__req_send_image_handler,
        }

    def start(self, request_count=5):
        """ Method the start configuration server """

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
        """ Method the listener client connections """

        self.logger.info('Start listen')
        while True:
            try:
                client, addr = self.socket.accept()
            except OSError:
                pass
            except Exception as ex:
                self.logger.error(ex)
            else:
                if addr in self.blacklist:
                    self.logger.warning(f'{addr} in blacklist')
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
        """ Method the handler of client requests """

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
        """ Method the sender of responses to clients """

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
            sleep(0.1)
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
        user = next(iter([u for u, c in self.users.items() if c == client]), None)
        if not user:
            self.blacklist.append(client.getpeername()[0])
            return
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
                answer = [Response(ANSWER, str(a)) for a in answer]
                answer.append(Response(ANSWER, None))
                return answer
                # answer = [str(a) for a in answer]
                # return Response(ANSWER, answer)
            elif answer is None:
                return Response(ANSWER, 'Done')
            return Response(ANSWER, answer)
        else:
            return Response(INCORRECT_REQUEST, 'Command not found')

    # region Request handlers

    @try_except_wrapper
    def __req_presence_handler(self, i_req, client, *args):
        """ Mathod the handler presence request """

        prv, pub = gen_keys()
        self.client_keys[i_req.body] = (client, prv)
        self.__send_to_client(client, Response(AUTH,
                                               pub.export_key().decode()))

    @try_except_wrapper
    def __req_auth_handler(self, i_req, client, *args):
        """ Mathod the handler authorization request """

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
        """ Mathod the handler start chat request """

        msg = Msg.from_dict(i_req.body)
        if msg.to not in self.users:
            self.logger.warning(f'{msg.to} not found')
            return
        self.__send_to_client(self.users[msg.to],
                              Response(START_CHAT, str(msg)))

    @try_except_wrapper
    def __req_accept_chat_handler(self, i_req, client, *args):
        """ Mathod the handler accept chat request """

        msg = Msg.from_dict(i_req.body)
        if msg.to not in self.users:
            self.logger.warning(f'{msg.to} not found')
            return
        self.__send_to_client(self.users[msg.to],
                              Response(ACCEPT_CHAT, str(msg)))

    @try_except_wrapper
    def __req_message_handler(self, i_req, client, *args):
        """ Mathod the handler message request """

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
        """ Mathod the handler command request """

        command, *args = i_req.body.split()
        user = [u for u, c in self.users.items() if c == client].pop()
        if len(args) < 1 or args[0] != user:
            args.insert(0, user)
        o_resp = self.__execute_command(command, *args)
        if isinstance(o_resp, list):
            [self.__send_to_client(client, r) for r in o_resp]
        else:
            self.__send_to_client(client, o_resp)

    @try_except_wrapper
    def __req_recv_image_handler(self, i_req, client, *args):
        user = [u for u, c in self.users.items() if c == client].pop()
        body = b64decode(i_req.body.encode())
        if user in self.images.keys():
            self.images[user] += body
        else:
            self.images[user] = body
        self.__send_to_client(client, Response(FILE_ANSWER))

    @try_except_wrapper
    def __req_end_recv_image_handler(self, i_req, client, *args):
        user = [u for u, c in self.users.items() if c == client].pop()
        if user not in self.images.keys():
            self.logger.warning('Image is empty')
            return
        user_avatar = self.images.pop(user)
        self.storage.set_avatar(user, user_avatar)
        self.__send_to_client(client, Response(FILE_ANSWER))
        # TODO send to all users updated avatar

    @try_except_wrapper
    def __req_send_image_handler(self, i_req, client, *args):
        avatar = self.storage.get_avatar(i_req.body)
        if avatar:
            sender_thread = ServerThread(lambda: self.__send_image_bytes(client, avatar), self.logger)
            sender_thread.start()
        else:
            self.__send_to_client(client, Response(FILE_ANSWER))

    @try_except_wrapper
    def __send_image_bytes(self, client, img_bytes):
        avatar_part = 512
        for i in range(0, len(img_bytes), avatar_part):
            part = b64encode(img_bytes[i:i + avatar_part])
            part_resp = Response(FILE_ANSWER, part.decode())
            self.__send_to_client(client, part_resp)
        self.__send_to_client(client, Response(FILE_ANSWER))

    # endregion
