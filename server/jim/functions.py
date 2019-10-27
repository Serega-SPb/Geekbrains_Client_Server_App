from base64 import b64encode, b64decode
import json
from jim.classes.package import *

ENCODING = 'utf-8'
BUFFER = 1024


def send_data(socket, data):
    data_dict = data.get_dict()
    js_str = json.dumps(data_dict)
    socket.send(b64encode(js_str.encode(ENCODING)))


def get_data(socket):
    data = b64decode(socket.recv(BUFFER))
    if not isinstance(data, bytes) or len(data) == 0:
        raise ValueError
    js_data = json.loads(data.decode(ENCODING))

    if js_data[TYPE] == REQUEST:
        return Request.from_dict(js_data)
    if js_data[TYPE] == RESPONSE:
        return Response.from_dict(js_data)
    raise ValueError
