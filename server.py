import argparse
from socket import *

from decorators import *
from jim.classes import *
from jim.constants import *
from jim.functions import *
import logging
import logs.server_log_config as log_config


class Server:

    TCP = (AF_INET, SOCK_STREAM)
    clients = []
    exit_flag = False
    socket = None

    def __init__(self, bind_addr, port):
        self.bind_addr = bind_addr
        self.port = port
        self.logger = logging.getLogger(log_config.LOGGER_NAME)

    @log_call_method
    def start(self, request_count=5):
        self.socket = socket(*self.TCP)
        self.socket.bind((self.bind_addr, self.port))
        self.logger.info(f'Config server port - {self.port}| Bind address - {self.bind_addr}')

        self.socket.listen(request_count)
        self.exit_flag = False
        self.listen()

    def stop(self):
        self.exit_flag = True

    @log_call_method
    def listen(self):
        self.logger.info('Start listen')
        while not self.exit_flag:
            client, addr = self.socket.accept()
            self.logger.info(f'Connection from {addr}')
            # wrapper(self.logger, self.listen_client, client)
            self.listen_client(client)
            self.logger.info(f'End connection {addr}')

    @try_except_wrapper
    @log_call_method
    def listen_client(self, client):
        while True:
            request = Request.from_dict(get_data(client))
            self.logger.info(request)
            if request.action == RequestAction.QUIT:
                client.close()
                return
            response = self.generate_response(request)
            self.logger.info(response)
            send_request(client, response)

    @try_except_wrapper
    @log_call_method
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
            self.logger.debug(f'Message: {body}')
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
