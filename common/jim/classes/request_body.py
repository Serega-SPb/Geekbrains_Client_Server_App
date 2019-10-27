import re

from jim.constants import USERNAME, PASSWORD, SENDER, TO, TEXT, MESSAGE


class BaseBody:

    def get_dict(self):
        return {s: str(getattr(self, s, None)) for s in self.__slots__}


class User(BaseBody):
    __slots__ = (USERNAME, PASSWORD)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_dict(self):
        return f'{self.username}:{self.password}'

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

    recv_pat = rf'^(?P<{SENDER}>[\w\d]*) to @(?P<{TO}>[\w]*): (?P<{TEXT}>(.|\n)*)'

    def __init__(self, text, sender, to='ALL'):
        self.text = text
        self.sender = sender
        self.to = to

    @classmethod
    def from_dict(cls, json_obj):
        ins = cls(json_obj[TEXT], json_obj[SENDER], json_obj[TO])
        return ins

    @classmethod
    def from_formated(cls, formated_text):
        match = re.match(cls.recv_pat, formated_text, re.MULTILINE)
        sender = match.group(SENDER)
        to = match.group(TO)
        msg = match.group(TEXT)
        return cls(msg, sender, to)

    def parse_msg(self):
        to_user = 'ALL'
        msg = self.text

        if '@' in msg:
            match = re.match(self.PATTERN, msg)
            to_user = match.group(TO)
            msg = match.group(MESSAGE)

        self.to = to_user
        self.text = msg.strip()

    def __str__(self):
        return f'{self.sender} to @{self.to}: {self.text}'
