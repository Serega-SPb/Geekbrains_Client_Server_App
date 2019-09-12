import argparse
import random
from socket import *

from common import *
from jim.classes import *
from jim.constants import *
from jim.functions import *


class Client:

    TCP = (AF_INET, SOCK_STREAM)
    USER = f'Test{random.randint(0,1000)}'

    def __init__(self, addr, port):
        self.socket = socket(*self.TCP)
        print_log(f'Connect to {addr}:{port}')
        self.socket.connect((addr, port))
        self.presence()

    def __del__(self):
        self.send_request(Request(RequestAction.QUIT, self.USER))

    def send_request(self, request):
        print(request)
        wrapper(send_request, self.socket, request)

    def get_response(self):
        response = wrapper(get_data, self.socket)
        if response is not None:
            response = Response.from_dict(response)
        print(response)
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
    parser.add_argument('addr', type=str, help='Server address')
    parser.add_argument('port', default=7777, type=int, nargs='?', help='Server port [default=7777]')

    args = parser.parse_args()

    addr = args.addr
    port = args.port

    if addr is None:
        print_error('Incorrect server address')
        return

    client = Client(addr, port)
    client.send_msg('Hello server')
    input('')


if __name__ == '__main__':
    main()
