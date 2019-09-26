import argparse
from socket import *
from select import select

from decorators import *
from jim.functions import *
import logging
import logs.server_log_config as log_config


class Server:

    __slots__ = ('bind_addr', 'port', 'logger', 'socket', 'clients', )

    TCP = (AF_INET, SOCK_STREAM)
    TIMEOUT = 5

    def __init__(self, bind_addr, port):
        self.bind_addr = bind_addr
        self.port = port
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        self.clients = []

    def start(self, request_count=5):
        self.socket = socket(*self.TCP)
        self.socket.settimeout(0.5)
        self.socket.bind((self.bind_addr, self.port))
        self.logger.info(f'Config server port - {self.port}| Bind address - {self.bind_addr}')

        self.socket.listen(request_count)
        self.__listen()

    def __listen(self):
        self.logger.info('Start listen')
        while True:
            try:
                client, addr = self.socket.accept()
            except OSError:
                pass
            except Exception as ex:
                self.logger.error(ex)
            else:
                self.logger.info(f'Connection from {addr}')
                self.clients.append(client)

            i_clients, o_clients = [], []
            try:
                i_clients, o_clients, ex = select(self.clients, self.clients, [], self.TIMEOUT)
            except OSError:
                pass
            except Exception as ex:
                self.logger.error(ex)

            requests = self.__get_requests(i_clients)
            if requests:
                self.__send_responses(requests, o_clients)

    @try_except_wrapper
    def __get_requests(self, i_clients):
        requests = {}
        for client in i_clients:
            try:
                requests[client] = get_data(client)
            except ConnectionError:
                self.clients.remove(client)
                self.logger.info(f'End connection {client}')
            except Exception as e:
                raise e
        return requests

    @try_except_wrapper
    def __send_responses(self, requests, o_clients):

        for soc, req in requests.items():
            resp = self.__generate_response(req)
            self.logger.info(soc)
            self.logger.info(resp)
            try:
                if req.action == RequestAction.QUIT:
                    raise ConnectionError
                send_request(soc, resp)
            except ConnectionError:
                self.logger.info(f'End connection {soc}')
                self.clients.remove(soc)
            except Exception as e:
                raise e

            for client in o_clients:
                if client == soc:
                    continue
                try:
                    send_request(client, req)
                except ConnectionError:
                    self.clients.remove(client)
                except Exception as e:
                    raise e

    @try_except_wrapper
    def __generate_response(self, request):
        action = request.action
        body = request.body

        if action == RequestAction.PRESENCE:
            return Response(OK)
        elif action == RequestAction.QUIT:
            return Response(OK)
        elif action == RequestAction.MESSAGE:
            msg = Msg.from_dict(body)
            self.logger.debug(f'Message: {str(msg)}')
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
