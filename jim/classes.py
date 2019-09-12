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

    def __str__(self):
        time = dt.fromtimestamp(self.time)
        return time.strftime("%d/%m/%y %H:%M:%S")


class Request(BasePackage):
    __slots__ = (ACTION, BODY)

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
        d = self.get_dict()
        return f'{super().__str__()} | REQUEST  | {str(d)}'


class Response(BasePackage):
    __slots__ = (CODE, MESSAGE)

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
        d = self.get_dict()
        return f'{super().__str__()} | RESPONSE | {str(d)}'
