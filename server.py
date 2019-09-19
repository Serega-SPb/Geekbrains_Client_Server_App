import argparse
from socket import *

from common import *
from jim.classes import *
from jim.constants import *
from jim.functions import *


class Server:

    TCP = (AF_INET, SOCK_STREAM)
    clients = []
    exit_flag = False
    socket = None

    def __init__(self, bind_addr, port):
        self.bind_addr = bind_addr
        self.port = port

    def start(self, request_count=5):
        self.socket = socket(*self.TCP)
        self.socket.bind((self.bind_addr, self.port))
        print_log(f'Config server port - {self.port}| Bind address - {self.bind_addr}')

        self.socket.listen(request_count)
        self.exit_flag = False
        self.listen()

    def stop(self):
        self.exit_flag = True

    def listen(self):
        print_log('Start listen')
        while not self.exit_flag:
            client, addr = self.socket.accept()
            print_log(f'Connection from {addr}')
            wrapper(self.listen_client, client)
            print_log(f'End connection {addr}')

    def listen_client(self, client):
        while True:
            request = Request.from_dict(get_data(client))
            print_log(request)
            if request.action == RequestAction.QUIT:
                client.close()
                return
            response = self.generate_response(request)
            send_request(client, response)

    def generate_response(self, request):
        action = request.action
        body = request.body

        if action == RequestAction.PRESENCE:
            user = body
            if user in self.clients:
                return Response(CONFLICT)
            self.clients.append(user)
            return Response(OK)
        elif action == RequestAction.QUIT:
            user = body
            self.clients.remove(user)
            return Response(OK)
        elif action == RequestAction.MESSAGE:
            print_log(f'Message: {body}')
            return Response(BASIC)
        return Response(INCORRECT_REQUEST)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=7777, type=int, nargs='?', help='Port [default=7777]')
    parser.add_argument('-a', '--addr', default='', type=str, nargs='?', help='Bind address')

    args = parser.parse_args()
    addr = args.addr
    port = args.port

    server = Server(addr, port)
    server.start()


if __name__ == '__main__':
    main()
