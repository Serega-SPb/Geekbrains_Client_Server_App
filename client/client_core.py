""" Module implements client connection and data exchange """

import logging
import queue
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from logs import client_log_config as log_config
from decorators import try_except_wrapper
from descriptors import Port
from jim.constants import RequestAction, RESPONSE
from jim.codes import OK, ANSWER, SERVER_ERROR, AUTH
from jim.classes.package import Request, Response
from jim.classes.request_body import User, Msg
from jim.functions import get_data, send_data
from client_crypt import encrypt_rsa, decrypt_rsa, \
                         import_pub_key, gen_keys, ClientCrypt
from client_db import ClientStorage
from ui.client_ui_logic import MessageBox


class ClientThread(Thread):
    """ Thread class for async execution the function of client """

    __slots__ = ('func', 'logger')

    def __init__(self, func, logger):
        super().__init__()
        self.func = func
        self.logger = logger
        self.daemon = True

    @try_except_wrapper
    def run(self):
        self.func()


def show_error(mes):
    """ Function for shows message on UI """
    # TODO Obsolete

    msb = MessageBox(mes)
    msb.show()
    msb.exec_()


class Client:
    """ Class client connection and data exchange """

    __slots__ = ('addr', '_port', 'user',
                 'logger', 'socket', 'connected',
                 'listener', 'sender', 'encryptors', 'priv_key',
                 'storage', 'subs', 'answers')

    TCP = (AF_INET, SOCK_STREAM)
    port = Port('_port')

    def __init__(self, addr, port):
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        self.addr = addr
        self.port = port
        self.connected = False
        self.subs = {}
        # self.subs = {201: [], 202: [], 203: [], 204: [], 205: []}
        self.answers = queue.Queue()
        self.encryptors = {}

    @property
    def username(self):
        return self.user.username

    def get_encryptor(self, contact):
        return self.encryptors[contact] if contact in self.encryptors else None

    def set_encryptor(self, contact, value):
        self.encryptors[contact] = value

    def set_user(self, username, password):
        self.user = User(username, password)
        self.storage = ClientStorage(username)

    def start(self):
        """ Method start connection to server """

        self.socket = socket(*self.TCP)
        start_txt = f'Connect to {self.addr}:{self.port} as {self.username}'
        self.logger.debug(start_txt)
        print(start_txt)
        self.__connect()

    @try_except_wrapper
    def __connect(self):
        self.socket.connect((self.addr, self.port))
        self.connected = True
        print('Done')
        response = self.authorization()
        if response.code != OK:
            show_error(str(response.message))
            self.logger.warning(response)
            exit()

        self.listener = ClientThread(self.__listen_server, self.logger)
        self.listener.start()

    @try_except_wrapper
    def __send_request(self, request):
        if not self.connected:
            return
        self.logger.debug(request)
        send_data(self.socket, request)

    @try_except_wrapper
    def __get_response(self):
        if not self.connected:
            return None
        response = get_data(self.socket)
        self.logger.debug(response)
        return response

    @try_except_wrapper
    def authorization(self):
        """ Method of authorization on server """
        pr_req = Request(RequestAction.PRESENCE, self.user.username)
        self.__send_request(pr_req)
        resp = self.__get_response()
        if resp is None:
            return Response(SERVER_ERROR)
        if resp.code != AUTH:
            return resp
        enc_pass = encrypt_rsa(
            import_pub_key(resp.message.encode()),
            self.user.password)
        auth_req = Request(RequestAction.AUTH, enc_pass.decode())
        self.__send_request(auth_req)
        return self.__get_response()

    def get_chat_req(self, contact):
        """ Method send request for gets all messages of chat with contact """

        req = Request(RequestAction.COMMAND,
                      f'get_chat {self.user.username} {contact}')
        self.__send_request(req)

    def get_users_req(self):
        """ Method send request for gets users online """

        self.__send_request(Request(RequestAction.COMMAND, 'get_users'))

    def get_contacts_req(self):
        """ Method send request for gets list contacts """

        self.__send_request(Request(RequestAction.COMMAND, 'get_contacts'))

    @try_except_wrapper
    def start_chat(self, contact):
        """ Method initialization of chat with contact """

        key = self.storage.get_key(contact)
        if key is not None:
            self.set_encryptor(contact, ClientCrypt(key))

        prv, pub = gen_keys()
        self.priv_key = prv
        msg = Msg(pub.export_key().decode(), self.username, contact)
        start_req = Request(RequestAction.START_CHAT, msg)
        self.__send_request(start_req)

    @try_except_wrapper
    def accepting_chat(self, resp_mes):
        """ Method of handle request to start chat """

        r_msg = Msg.from_formated(resp_mes)
        pub = import_pub_key(r_msg.text.encode())

        key = self.storage.get_key(r_msg.sender)
        if key is not None:
            encryptor = ClientCrypt(key)
        else:
            encryptor = ClientCrypt.gen_secret(self.username, r_msg.sender)
            self.storage.add_chat_key(r_msg.sender, encryptor.secret)
        self.set_encryptor(r_msg.sender, encryptor)
        enc_key = encrypt_rsa(pub, encryptor.secret)
        msg = Msg(enc_key.decode(), self.username, r_msg.sender)
        accept_req = Request(RequestAction.ACCEPT_CHAT, msg)
        self.__send_request(accept_req)

    @try_except_wrapper
    def accepted_chat(self, resp_mes):
        """ Method of handle response about confirm start of chat """

        msg = Msg.from_formated(resp_mes)
        encryptor = self.get_encryptor(msg.sender)
        if encryptor is not None:
            return
        secret = decrypt_rsa(self.priv_key, msg.text.encode())
        self.set_encryptor(msg.sender, ClientCrypt(secret))
        self.storage.add_chat_key(msg.sender, secret)

    def add_contact(self, contact):
        """ Method add contact in contact list """

        if self.storage.get_contact(contact):
            return False
        self.storage.add_contact(contact)
        req = Request(RequestAction.COMMAND, f'add_contact {contact}')
        self.__send_request(req)
        return True

    def rem_contact(self, contact):
        """ Method remove contact from contact list """

        self.storage.remove_contact(contact)
        req = Request(RequestAction.COMMAND, f'rem_contact {contact}')
        self.__send_request(req)

    def sync_contacts(self, contacts):
        """ Method sync of list contact from server to client """

        for contact in contacts:
            self.storage.append_contact(contact)

    @try_except_wrapper
    def send_msg(self, text, to):
        """ Method send messge to server """

        encryptor = self.get_encryptor(to)
        text = encryptor.encript_msg(text.encode()).decode()
        msg = Msg(text, self.user, to)
        self.storage.add_message(msg.to, msg.text)
        request = Request(RequestAction.MESSAGE, msg)
        self.__send_request(request)

    def __listen_server(self):
        """ Method listen responses from server """

        while self.connected:
            resp = get_data(self.socket)
            self.logger.debug(resp)
            if resp.type != RESPONSE:
                self.logger.warning(f'Received not RESPONSE:\n {resp}')
                continue
            if resp.code == ANSWER:
                self.answers.put(resp.message)
                print(f'server: {resp.message}')
            elif resp.code in self.subs.keys():
                for sub in self.subs[resp.code]:
                    sub(resp.message)
            else:
                print(resp.message)

    def subscribe(self, code, func):
        """ Method subscribe of function to response code """

        if code in self.subs.keys():
            self.subs[code].append(func)
        else:
            self.subs[code] = [func]

    def parse_recv_message(self, msg):
        """ Method parse/decrypt message """

        msg = Msg.from_formated(msg)
        encryptor = self.get_encryptor(msg.sender)
        msg.text = encryptor.decrypt_msg(msg.text.encode()).decode()
        return msg.sender, msg.text
