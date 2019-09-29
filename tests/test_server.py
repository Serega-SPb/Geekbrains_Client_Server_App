import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))

from unittest import TestCase, main

from server import Server
from jim.classes import *
from jim.constants import *


class TestServer(TestCase):

    def setUp(self):
        self.server = Server('', 0)

        self.response_ok = Response(OK)
        self.response_ok.time = 1.1

        self.response_basic = Response(BASIC)
        self.response_basic.time = 1.1

        self.response_incorrect = Response(INCORRECT_REQUEST)
        self.response_incorrect.time = 1.1

        self.response_conflict = Response(CONFLICT)
        self.response_conflict.time = 1.1

    def test_request_presence(self):
        response = self.server.__generate_response(Request(RequestAction.PRESENCE))
        response.time = 1.1
        self.assertEqual(response, self.response_ok)

    def test_request_quit(self):
        response = self.server.__generate_response(Request(RequestAction.QUIT))
        response.time = 1.1
        self.assertEqual(response, self.response_ok)

    def test_request_message(self):
        response = self.server.__generate_response(Request(RequestAction.MESSAGE))
        response.time = 1.1
        self.assertEqual(response, self.response_basic)

    def test_request_incorrect(self):
        response = self.server.__generate_response(Request('test'))
        response.time = 1.1
        self.assertEqual(response, self.response_incorrect)

    def test_request_empty(self):
        response = self.server.__generate_response(Request(None))
        response.time = 1.1
        self.assertEqual(response, self.response_incorrect)

    def test_request_presence_conflict(self):
        self.server.__generate_response(Request(RequestAction.PRESENCE, 'test'))
        response = self.server.__generate_response(Request(RequestAction.PRESENCE, 'test'))
        response.time = 1.1
        self.assertEqual(response, self.response_conflict)


if __name__ == '__main__':
    main()
