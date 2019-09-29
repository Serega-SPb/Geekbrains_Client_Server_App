import re
from datetime import datetime as dt
from jim.constants import *

TYPE = 'type'
REQUEST = 'request'
RESPONSE = 'response'

ACTION = 'action'
TIME = 'time'
BODY = 'body'
CODE = 'code'
MESSAGE = 'message'

USERNAME = 'username'
SENDER = 'sender'
TO = 'to'
TEXT = 'text'


class Code:
    __slots__ = (CODE, MESSAGE)

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __eq__(self, other: int):
        return self.code == other

    def __str__(self):
        return f'{self.code} - {self.message}'


class BasePackage:
    __slots__ = (TIME, TYPE)

    def __init__(self):
        super().__init__()
        self.time = dt.timestamp(dt.now())

    def get_dict(self):
        return {s: getattr(self, s, None) for s in self.__slots__}


class Request(BasePackage):
    __slots__ = (ACTION, BODY, TIME, TYPE)

    def __init__(self, action, body=''):
        super().__init__()
        self.type = REQUEST
        self.action = action
        self.body = body

    @classmethod
    def from_dict(cls, json_obj):
        ins = cls(json_obj[ACTION], json_obj[BODY])
        if TIME in json_obj:
            ins.time = json_obj[TIME]
        return ins

    def get_dict(self):
        d = super().get_dict()
        b = d[BODY]
        if b and isinstance(b, BaseBody):
            d[BODY] = (d[BODY]).get_dict()
        return d

    def __str__(self):
        return f'REQUEST  | {str(self.get_dict())}'

    def __eq__(self, other):
        if not isinstance(other, Request):
            return False
        if other.action != self.action:
            return False
        if other.body != self.body:
            return False
        if other.time != self.time:
            return False
        return True


class Response(BasePackage):
    __slots__ = (CODE, MESSAGE, TIME, TYPE)

    def __init__(self, code):
        super().__init__()
        self.type = RESPONSE
        self.code = code.code
        self.message = code.message

    @classmethod
    def from_dict(cls, json_obj):
        ins = cls(Code(json_obj[CODE], json_obj[MESSAGE]))
        if TIME in json_obj:
            ins.time = json_obj[TIME]
        return ins

    def __str__(self):
        return f'RESPONSE | {str(self.get_dict())}'

    def __eq__(self, other):
        if not isinstance(other, Response):
            return False
        if other.code != self.code:
            return False
        if other.message != self.message:
            return False
        if other.time != self.time:
            return False
        return True


class BaseBody:

    def get_dict(self):
        return {s: str(getattr(self, s, None)) for s in self.__slots__}


class User(BaseBody):
    __slots__ = (USERNAME,)

    def __init__(self, username):
        self.username = username

    def get_dict(self):
        return self.username

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        if other.username != self.username:
            return False
        return True

    def __str__(self):
        return self.username


class Msg(BaseBody):
    __slots__ = (SENDER, TO, TEXT)

    PATTERN = r'@(?P<to>[\w\d]*)?(?P<message>.*)'

    def __init__(self, text, sender, to='ALL'):
        self.text = text
        self.sender = sender
        self.to = to

    @classmethod
    def from_dict(cls, json_obj):
        ins = cls(json_obj[TEXT], json_obj[SENDER], json_obj[TO])
        return ins

    def parse_msg(self):
        to_user = 'ALL'
        msg = self.text

        if '@' in msg:
            match = re.match(self.PATTERN, msg)
            to_user = match.group(TO)
            msg = match.group(MESSAGE)

        self.to = to_user
        self.text = msg

    def __str__(self):
        return f'{self.sender} to @{self.to}: {self.text}'
