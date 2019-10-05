import re

from jim.constants import *


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
