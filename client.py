import argparse
import random
from socket import *
from threading import Thread

from decorators import *
from jim.codes import *
from jim.classes.request_body import *
from jim.functions import *
import logging
import logs.client_log_config as log_config


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


class Client:
    __slots__ = ('addr', 'port', 'logger', 'socket', 'connected', 'listener', 'sender')

    TCP = (AF_INET, SOCK_STREAM)
    USER = User(f'Test{random.randint(0,1000)}')

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
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
        self.__print_help()
        response = self.presence()
        if response.code != OK:
            self.logger.warning(response)
            return

        self.listener = ClientThread(self.__listen_server, self.logger)
        self.listener.start()

        self.sender = ClientThread(self.send_msg, self.logger)
        self.sender.start()

        self.sender.join()
        # self.send_msg()

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
            if msg.lower() == 'help':
                self.__print_help()
                continue

            if msg.upper() == 'Q':
                break
            msg = Msg(msg, self.USER)
            msg.parse_msg()
            request = Request(RequestAction.MESSAGE, msg)
            self.__send_request(request)

    def __listen_server(self):
        while self.connected:
            msg = get_data(self.socket)
            if msg.type == REQUEST:
                self.__print_request(msg)

    def __print_request(self, request):
        if request.action == RequestAction.PRESENCE:
            print(f'{request.body} connected')
        if request.action == RequestAction.QUIT:
            print(f'{request.body} disconnected')
        if request.action == RequestAction.MESSAGE:
            print(str(Msg.from_dict(request.body)))
        else:
            self.logger.debug(request)

    def __print_help(self):
        txt = 'Commands:\n' \
              'help - print command list\n' \
              'q - quit\n' \
              '@<username> - message to <username>\n' \
              '@server get_users - get connected users\n'
        print(txt)


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
