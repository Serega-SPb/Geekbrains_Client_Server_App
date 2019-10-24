import argparse
import logging
import queue
import random
from socket import *
from threading import Thread

import logs.client_log_config as log_config
from common.decorators import *
from common.descriptors import Port
from jim.codes import *
from jim.classes.request_body import *
from jim.functions import *
from client_db import ClientStorage
# from metaclasses import ClientVerifier
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


def print_help():
    txt = 'Commands:\n' \
          '!<command> - execute local(client) command\n' \
          '@<username> - message to <username>\n' \
          '#<command> <args> - send command to server\n' \
          'q - quit\n'
    print(txt)


class Client:
    __slots__ = ('addr', '_port', 'logger', 'socket', 'connected', 'listener', 'sender', 'storage', 'subs', 'answers')

    TCP = (AF_INET, SOCK_STREAM)
    USER = User(f'Test{random.randint(0, 1000)}')

    port = Port('_port')

    def __init__(self, addr, port):
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        self.addr = addr
        self.port = port
        self.connected = False
        self.subs = {201: [], 202: [], 203: []}
        self.answers = queue.Queue()
        self.__reg_resp_console()
        # name = input('Set name (enter generate name):\n')
        # if len(name) > 0:
        #     self.USER.username = name
        # self.storage = ClientStorage(self.USER.username)

    @property
    def username(self):
        return self.USER.username

    @username.setter
    def username(self, value):
        self.USER.username = value
        self.storage = ClientStorage(self.USER.username)

    def start(self):
        self.socket = socket(*self.TCP)
        start_txt = f'Connect to {self.addr}:{self.port} as {self.USER}...'
        self.logger.debug(start_txt)
        print(start_txt)
        self.__connect()

    def __reg_resp_console(self):
        self.subscribe(201, lambda m: print(f'{m} connected'))
        self.subscribe(202, lambda m: print(f'{m} disconnected'))
        self.subscribe(203, lambda m: print(m))

    @try_except_wrapper
    def __connect(self):
        self.socket.connect((self.addr, self.port))
        self.connected = True
        print('Done')
        print_help()
        response = self.presence()
        if response.code != OK:
            self.logger.warning(response)
            return

        self.listener = ClientThread(self.__listen_server, self.logger)
        self.listener.start()

        # self.__console()

        # self.sender = ClientThread(self.send_msg, self.logger)
        # self.sender.start()
        # self.sender.join()

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

    def presence(self):
        request = Request(RequestAction.PRESENCE, self.USER)
        self.__send_request(request)
        return self.__get_response()

    def __console(self):
        while self.connected:
            msg = input('Enter message:\n')
            if msg.upper() == 'Q':
                break
            if msg[0] == '!':
                self.__execute_local_command(msg[1:])
                continue
            if msg[0] == '#':
                request = Request(RequestAction.COMMAND, msg[1:])
                self.parse_command(request.body)
            else:
                msg = Msg(msg, self.USER)
                msg.parse_msg()
                self.storage.add_message(msg.to, msg.text)
                request = Request(RequestAction.MESSAGE, msg)
            self.__send_request(request)

    def get_chat_req(self, contact):
        req = Request(RequestAction.COMMAND, f'get_chat {self.USER.username} {contact}')
        self.__send_request(req)

    def get_users_req(self):
        self.__send_request(Request(RequestAction.COMMAND, 'get_users'))

    def get_contacts_req(self):
        self.__send_request(Request(RequestAction.COMMAND, 'get_contacts'))

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

    def send_msg(self, text, to):
        msg = Msg(text, self.USER, to)
        self.storage.add_message(msg.to, msg.text)
        request = Request(RequestAction.MESSAGE, msg)
        self.__send_request(request)

    def parse_command(self, command):
        command, *args = command.split(' ')
        if command == 'add_contact':
            self.storage.add_contact(args[0])
        elif command == 'rem_contact':
            self.storage.remove_contact(args[0])

    def __execute_local_command(self, command):
        if command == 'help':
            print_help()
        elif command == 'set_name':
            name = input('Set new name')
            self.USER.username = name
            self.__send_request(Request(RequestAction.PRESENCE, self.USER))
        elif command == 'reconnect':
            self.start()
        else:
            print('Command not found')

    def __listen_server(self):
        while self.connected:
            resp = get_data(self.socket)
            self.logger.debug(resp)
            if resp.type != RESPONSE:
                self.logger.warning(f'Received not RESPONSE:\n {resp}')
                continue
            if resp.code == 101:
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
    client.username = login.username
    client.start()
    win = MainWindow(client)
    win.setWindowTitle(client.username)
    win.show()
    app.exec_()


if __name__ == '__main__':
    main()
