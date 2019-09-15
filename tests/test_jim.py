import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))

from unittest import TestCase, main

from jim.classes import *
from jim.constants import *
from jim.functions import *


class TestJimClasses(TestCase):

    def test_request_dict(self):
        body = 'test'
        time = dt.timestamp(dt.now())

        request = Request(RequestAction.PRESENCE, body)
        self.assertEqual(request.get_dict(), {ACTION: RequestAction.PRESENCE, TIME: time, BODY: body})

        request = Request(RequestAction.QUIT)
        self.assertEqual(request.get_dict(), {ACTION: RequestAction.QUIT, TIME: time, BODY: ''})

        self.assertRaises(TypeError, Request)

    def test_response_dict(self):
        time = dt.timestamp(dt.now())

        response = Response(OK)
        self.assertEqual(response.get_dict(), {CODE: 200, TIME: time, MESSAGE: 'OK'})

        self.assertRaises(TypeError, Response)


class TestJimFunctions(TestCase):

    class TestSocket:
        encoded_data = None
        request = None

        def __init__(self, data):
            self.data = data

        def send(self, request):
            json_str = json.dumps(self.data)
            self.encoded_data = json_str.encode(ENCODING)
            self.request = request

        def recv(self, buf):
            json_str = json.dumps(self.data)
            return json_str.encode(ENCODING)

    def test_send_request(self):
        request = Request(RequestAction.MESSAGE)
        socket = self.TestSocket(request.get_dict())
        send_request(socket, request)
        self.assertEqual(socket.encoded_data, socket.request)

    def test_get_data(self):
        response = Response(BASIC)
        socket = self.TestSocket(response.get_dict())
        self.assertEqual(get_data(socket), response.get_dict())
        self.assertEqual(Response.from_dict(get_data(socket)), response)


if __name__ == '__main__':
    main()
