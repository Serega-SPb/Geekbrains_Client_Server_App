""" Module of constants used in jim protocol """

TYPE = 'type'
REQUEST = 'request'
RESPONSE = 'response'

ACTION = 'action'
TIME = 'time'
BODY = 'body'
CODE = 'code'
MESSAGE = 'message'
USERNAME = 'username'
PASSWORD = 'password'
SENDER = 'sender'
TO = 'to'
TEXT = 'text'


class RequestAction:
    """ Class the storage of request actions """

    PRESENCE = 'presence'
    AUTH = 'auth'
    MESSAGE = 'msg'
    QUIT = 'quit'
    COMMAND = 'command'
    START_CHAT = 'start_chat'
    ACCEPT_CHAT = 'accept_chat'
    IMAGE = 'image'
    END_IMAGE = 'end_image'
    GET_IMAGE = 'get_image'
