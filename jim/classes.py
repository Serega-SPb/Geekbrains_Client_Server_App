from datetime import datetime as dt

ACTION = 'action'
TIME = 'time'
BODY = 'body'
CODE = 'code'
MESSAGE = 'message'


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

    __slots__ = (TIME,)

    def __init__(self):
        self.time = dt.timestamp(dt.now())

    def get_dict(self):
        return {s: getattr(self, s, None) for s in self.__slots__}


class Request(BasePackage):
    __slots__ = (ACTION, BODY, TIME)

    def __init__(self, action, body=''):
        super().__init__()
        self.action = action
        self.body = body

    @classmethod
    def from_dict(cls, json_obj):
        ins = cls(json_obj[ACTION], json_obj[BODY])
        if TIME in json_obj:
            ins.time = json_obj[TIME]
        return ins

    def __str__(self):
        return f'REQUEST  | {str(self.get_dict())}'

    def __eq__(self, other):
        if not isinstance(other, Request):
            return False
        elif other.action != self.action:
            return False
        elif other.body != self.body:
            return False
        elif other.time != self.time:
            return False
        return True


class Response(BasePackage):
    __slots__ = (CODE, MESSAGE, TIME)

    def __init__(self, code):
        super().__init__()
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
        elif other.code != self.code:
            return False
        elif other.message != self.message:
            return False
        elif other.time != self.time:
            return False
        return True
