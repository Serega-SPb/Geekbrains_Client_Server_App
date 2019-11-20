import asyncio
import threading
from base64 import b64encode, b64decode

from descriptors import Port


class ServerAsync:

    BUFFER = 1024
    port = Port('_port')

    def __init__(self, loop, bind_addr, port, request_handler):
        self.loop = loop
        self.addr = bind_addr
        self.port = port
        self.request_handler = request_handler
        self.request_decoder = lambda x: x.decode()
        self.response_encoder = lambda x: x.encode()

    def set_request_decoder(self, value):
        self.request_decoder = value

    def set_response_encoder(self, value):
        self.response_encoder = value

    async def start(self):
        self.server_cor = \
            asyncio.start_server(self.connection_handler, self.addr, self.port, loop=self.loop)
        self.server = await self.server_cor

    def start_background(self):
        back_lamd = lambda: self.loop.run_until_complete(self.__setup_back())
        self.back_thread = threading.Thread(target=back_lamd, daemon=True)
        self.back_thread.start()

    async def __setup_back(self):
        asyncio.set_event_loop(self.loop)
        await self.start()
        await self.server.wait_closed()

    async def connection_handler(self, reader, writer):
        while True:
            try:
                data = await reader.read(self.BUFFER)
                addr = writer.get_extra_info('peername')

                data = self.request_decoder(data)
                print(f'{addr} REQUEST: {data}')
                resp = self.request_handler(data)

                print(f'RESPONCE: {resp}')
                resp = self.response_encoder(resp)
                writer.write(resp)
                await writer.drain()
            except Exception as e:
                print(e)
                return

    def stop(self):
        self.server.close()


ENCODING = 'utf-8'


def client_handler(req):
    print(f'<<< {req}')
    return f'RESP {req}'


def encoder(data):
    return b64encode(data.encode(ENCODING))


def decoder(data):
    return b64decode(data).decode(ENCODING)


def main():
    loop = asyncio.get_event_loop()
    server = ServerAsync(loop, '', 7878, client_handler)
    server.set_response_encoder(encoder)
    server.set_request_decoder(decoder)
    server.start_background()
    while True:
        msg = input()
        if msg == 'q':
            break


if __name__ == '__main__':
    main()
