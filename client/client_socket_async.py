import asyncio
import threading
from base64 import b64encode, b64decode

from descriptors import Port


class ClientAsync:

    BUFFER = 1024
    port = Port('_port')

    def __init__(self, loop, addr, port, response_handler):
        self.loop = loop
        self.addr = addr
        self.port = port
        self.response_handler = response_handler
        self.response_decoder = lambda x: x.decode()
        self.request_encoder = lambda x: x.encode()

    def set_response_decoder(self, value):
        self.response_decoder = value

    def set_request_encoder(self, value):
        self.request_encoder = value

    def start_background(self):
        back_lamd = lambda: self.loop.run_until_complete(self.__setup_back())
        self.back_thread = threading.Thread(target=back_lamd, daemon=True)
        self.back_thread.start()

    async def __setup_back(self):
        try:
            asyncio.set_event_loop(self.loop)
            await self.connect()
            await asyncio.gather(self.send(), self.read())
        except Exception as e:
            print(e)

    async def connect(self):
        self.reader, self.writer = \
            await asyncio.open_connection(self.addr, self.port, loop=self.loop)
        print('\rconnected\n')

    async def read(self):
        while True:
            try:
                resp = await self.reader.read(self.BUFFER)
                resp = self.response_decoder(resp)
                print(f'RESPONCE: {resp}')
                self.response_handler(resp)
            except Exception as e:
                print(f'ER: {e}')
                return

    async def send(self):
        while True:
            req = await self.input_.get()
            print(f'REQUEST: {req}')
            req = self.request_encoder(req)
            self.writer.write(req)
            await self.writer.drain()


ENCODING = 'utf-8'


def listen(data):
    print(f'<<< {data}')


def encoder(data):
    return b64encode(data.encode(ENCODING))


def decoder(data):
    return b64decode(data).decode(ENCODING)


def main():
    event_loop = asyncio.get_event_loop()
    input_queue = asyncio.Queue(loop=event_loop)
    client = ClientAsync(event_loop, '127.0.0.1', 7878, listen)
    client.input_ = input_queue
    client.set_request_encoder(encoder)
    client.set_response_decoder(decoder)
    client.start_background()

    while True:
        msg = input('>>> ')
        if msg == 'q':
            break
        asyncio.run_coroutine_threadsafe(input_queue.put(msg), event_loop)


if __name__ == '__main__':
    main()
