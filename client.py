import argparse
import logging
import random
from socket import *
from threading import Thread

import logs.client_log_config as log_config
from decorators import *
from descriptors import Port
from jim.codes import *
from jim.classes.request_body import *
from jim.functions import *
# from metaclasses import ClientVerifier


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
    __slots__ = ('addr', '_port', 'logger', 'socket', 'connected', 'listener', 'sender')

    TCP = (AF_INET, SOCK_STREAM)
    USER = User(f'Test{random.randint(0, 1000)}')

    port = Port('_port')

    def __init__(self, addr, port):
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        self.addr = addr
        self.port = port
        self.connected = False

    def start(self):
        self.socket = socket(*self.TCP)
        start_txt = f'Connect to {self.addr}:{self.port} as {self.USER}...'
        self.logger.debug(start_txt)
        print(start_txt)
        self.__connect()

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

        self.send_msg()

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

    def send_msg(self):
        while self.connected:
            msg = input('Enter message:\n')
            if msg.upper() == 'Q':
                break
            if msg[0] == '!':
                self.__execute_local_command(msg[1:])
                continue
            if msg[0] == '#':
                request = Request(RequestAction.COMMAND, msg[1:])
            else:
                msg = Msg(msg, self.USER)
                msg.parse_msg()
                request = Request(RequestAction.MESSAGE, msg)
            self.__send_request(request)

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
                print(f'server: {resp.message}')
            else:
                print(resp.message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default='localhost', type=str, nargs='?', help='Server address [default=localhost]')
    parser.add_argument('port', default=7777, type=int, nargs='?', help='Server port [default=7777]')

    args = parser.parse_args()

    addr = args.addr
    port = args.port

    client = Client(addr, port)
    client.start()


if __name__ == '__main__':
    main()
