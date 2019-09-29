import argparse
import random
from socket import *
from threading import Thread

from decorators import *
from jim.functions import *
import logging
import logs.client_log_config as log_config


class Client:

    __slots__ = ('addr', 'port', 'logger', 'socket', 'connected', 'mode', 'listener', 'sender')

    TCP = (AF_INET, SOCK_STREAM)
    USER = User(f'Test{random.randint(0,1000)}')

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        self.connected = False

    def start(self, mode='L'):
        self.socket = socket(*self.TCP)
        self.mode = mode
        self.logger.info(f'Connect to {self.addr}:{self.port}')
        self.__connect()
        # wrapper(self.logger, self.connect)

    @try_except_wrapper
    def __connect(self):
        self.socket.connect((self.addr, self.port))
        self.connected = True
        self.presence()

        # if self.mode == 'S':
        #     self.send_msg()
        # elif self.mode == 'L':
        #     self.__listen_server()

        self.listener = Thread(target=self.__listen_server)
        self.sender = Thread(target=self.send_msg)

        self.listener.start()
        self.sender.start()

        self.listener.join()
        self.sender.join()

    def disconnect(self):
        self.connected = False
        self.__send_request(Request(RequestAction.QUIT, self.USER))

    def __del__(self):
        self.disconnect()

    @try_except_wrapper
    def __send_request(self, request):
        if not self.connected:
            return
        self.logger.debug(request)
        send_request(self.socket, request)

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
        response = self.__get_response()

    def send_msg(self):

        while self.connected:
            msg = input('Enter message:\n')
            if msg == 'Q':
                break

            request = Request(RequestAction.MESSAGE, Msg(msg, self.USER))
            self.__send_request(request)

    def __listen_server(self):
        while self.connected:
            msg = get_data(self.socket)
            if msg.type == REQUEST:
                self.print_request(msg)

    def print_request(self, request):
        if request.action == RequestAction.PRESENCE:
            print(f'{request.body} connected')
        if request.action == RequestAction.QUIT:
            print(f'{request.body} disconnected')
        if request.action == RequestAction.MESSAGE:
            print(str(Msg.from_dict(request.body)))
        else:
            self.logger.debug(request)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default='localhost', type=str, nargs='?', help='Server address [default=localhost]')
    parser.add_argument('port', default=7777, type=int, nargs='?', help='Server port [default=7777]')
    parser.add_argument('mode', default='L', type=str, nargs='?', help='Client mode [default=L]')

    args = parser.parse_args()

    addr = args.addr
    port = args.port
    mode = args.mode

    client = Client(addr, port)
    client.start(mode.upper())
    # client.send_msg()
    # client.send_msg('Hello server')


if __name__ == '__main__':
    main()
