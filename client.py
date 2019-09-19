import argparse
import random
from socket import *

from common import *
from jim.classes import *
from jim.constants import *
from jim.functions import *
import logging
import logs.client_log_config as log_config


class Client:

    TCP = (AF_INET, SOCK_STREAM)
    USER = f'Test{random.randint(0,1000)}'
    connected = False
    socket = None

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.logger = logging.getLogger(log_config.LOGGER_NAME)

    def start(self):
        self.socket = socket(*self.TCP)
        self.logger.info(f'Connect to {self.addr}:{self.port}')
        wrapper(self.logger, self.connect)

    def connect(self):
        self.socket.connect((self.addr, self.port))
        self.connected = True
        self.presence()

    def __del__(self):
        self.send_request(Request(RequestAction.QUIT, self.USER))

    def send_request(self, request):
        if not self.connected:
            return
        self.logger.info(request)
        wrapper(self.logger, send_request, self.socket, request)

    def get_response(self):
        if not self.connected:
            return
        response = wrapper(self.logger, get_data, self.socket)
        if response is not None:
            response = Response.from_dict(response)
        self.logger.info(response)
        return response

    def presence(self):
        request = Request(RequestAction.PRESENCE, self.USER)
        self.send_request(request)
        response = self.get_response()

    def send_msg(self, msg):
        request = Request(RequestAction.MESSAGE, msg)
        self.send_request(request)
        response = self.get_response()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default='localhost', type=str, nargs='?', help='Server address')
    parser.add_argument('port', default=7777, type=int, nargs='?', help='Server port [default=7777]')

    args = parser.parse_args()

    addr = args.addr
    port = args.port

    client = Client(addr, port)
    client.start()
    client.send_msg('Hello server')
    input('')


if __name__ == '__main__':
    main()
