import argparse
import logging
import queue
import random
import sys
from socket import *
from threading import Thread

sys.path.append('../')

import logs.client_log_config as log_config
from common.decorators import *
from common.descriptors import Port
from jim.codes import *
from jim.classes.request_body import *
from jim.functions import *
from client_crypt import *
from client_db import ClientStorage
from ui.client_ui_logic import *


class ClientThread(Thread):
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
    msb = MessageBox(mes)
    msb.show()
    msb.exec_()


class Client:
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
        self.subs = {201: [], 202: [], 203: [], 204: [], 205: []}
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
        self.socket = socket(*self.TCP)
        start_txt = f'Connect to {self.addr}:{self.port} as {self.user.username}...'
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
            return

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
            return
        response = get_data(self.socket)
        self.logger.debug(response)
        return response

    @try_except_wrapper
    def authorization(self):
        pr_req = Request(RequestAction.PRESENCE, self.user.username)
        self.__send_request(pr_req)
        resp = self.__get_response()
        if resp is None:
            return Response(SERVER_ERROR)
        if resp.code != AUTH:
            return resp
        enc_pass = encrypt_rsa(import_pub_key(resp.message.encode()), self.user.password)
        auth_req = Request(RequestAction.AUTH, enc_pass.decode())
        self.__send_request(auth_req)
        return self.__get_response()

    def get_chat_req(self, contact):
        req = Request(RequestAction.COMMAND, f'get_chat {self.user.username} {contact}')
        self.__send_request(req)

    def get_users_req(self):
        self.__send_request(Request(RequestAction.COMMAND, 'get_users'))

    def get_contacts_req(self):
        self.__send_request(Request(RequestAction.COMMAND, 'get_contacts'))

    @try_except_wrapper
    def start_chat(self, contact):
        key = self.storage.get_key(contact)
        if key is not None:
            self.set_encryptor(contact, ClientCrypt(key))
            # self.encryptor = ClientCrypt(key)

        prv, pub = gen_keys()
        self.priv_key = prv
        msg = Msg(pub.export_key().decode(), self.username, contact)
        start_req = Request(RequestAction.START_CHAT, msg)
        self.__send_request(start_req)

    @try_except_wrapper
    def accepting_chat(self, resp_mes):
        r_msg = Msg.from_formated(resp_mes)
        pub = import_pub_key(r_msg.text.encode())

        key = self.storage.get_key(r_msg.sender)
        if key is not None:
            encryptor = ClientCrypt(key)
            # self.encryptor = ClientCrypt(key)
        else:
            # self.encryptor = ClientCrypt.gen_secret(self.username, r_msg.sender)
            encryptor = ClientCrypt.gen_secret(self.username, r_msg.sender)
            self.storage.add_chat_key(r_msg.sender, encryptor.secret)
        self.set_encryptor(r_msg.sender, encryptor)
        enc_key = encrypt_rsa(pub, encryptor.secret)
        msg = Msg(enc_key.decode(), self.username, r_msg.sender)
        accept_req = Request(RequestAction.ACCEPT_CHAT, msg)
        self.__send_request(accept_req)

    @try_except_wrapper
    def accepted_chat(self, resp_mes):
        msg = Msg.from_formated(resp_mes)
        encryptor = self.get_encryptor(msg.sender)
        if encryptor is not None:
            return

        secret = decrypt_rsa(self.priv_key, msg.text.encode())
        self.set_encryptor(msg.sender, ClientCrypt(secret))
        self.storage.add_chat_key(msg.sender, secret)

    def add_contact(self, contact):
        if self.storage.get_contact(contact):
            return False
        self.storage.add_contact(contact)
        req = Request(RequestAction.COMMAND, f'add_contact {contact}')
        self.__send_request(req)

    def rem_contact(self, contact):
        self.storage.remove_contact(contact)
        req = Request(RequestAction.COMMAND, f'rem_contact {contact}')
        self.__send_request(req)

    def sync_contacts(self, contacts):
        for c in contacts:
            self.storage.append_contact(c)

    @try_except_wrapper
    def send_msg(self, text, to):
        encryptor = self.get_encryptor(to)
        text = encryptor.encript_msg(text.encode()).decode()
        msg = Msg(text, self.user, to)
        self.storage.add_message(msg.to, msg.text)
        request = Request(RequestAction.MESSAGE, msg)
        self.__send_request(request)

    def __listen_server(self):
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
                for s in self.subs[resp.code]:
                    s(resp.message)
            else:
                print(resp.message)

    def subscribe(self, code, func):
        if code in self.subs.keys():
            self.subs[code].append(func)
        else:
            self[code] = [func]

    def parse_recv_message(self, msg):
        msg = Msg.from_formated(msg)
        encryptor = self.get_encryptor(msg.sender)
        msg.text = encryptor.decrypt_msg(msg.text.encode()).decode()
        return msg.sender, msg.text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default='localhost', type=str, nargs='?', help='Server address [default=localhost]')
    parser.add_argument('port', default=7777, type=int, nargs='?', help='Server port [default=7777]')

    args = parser.parse_args()

    addr = args.addr
    port = args.port

    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    app.exec_()

    if not login.start:
        return
    login.close()

    client = Client(addr, port)
    client.set_user(login.username, login.password)
    client.start()
    win = MainWindow(client)
    win.setWindowTitle(client.username)
    win.show()
    app.exec_()


if __name__ == '__main__':
    main()
