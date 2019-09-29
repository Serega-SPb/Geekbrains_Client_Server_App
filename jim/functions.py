import json
from jim.classes import *

ENCODING = 'utf-8'
BUFFER = 512


def send_request(socket, request):
    request_dict = request.get_dict()
    js_str = json.dumps(request_dict)
    socket.send(js_str.encode(ENCODING))


def get_data(socket):
    data = socket.recv(BUFFER)
    if not isinstance(data, bytes):
        raise ValueError
    js_data = json.loads(data.decode(ENCODING))

    if js_data[TYPE] == REQUEST:
        return Request.from_dict(js_data)
    if js_data[TYPE] == RESPONSE:
        return Response.from_dict(js_data)
    raise ValueError
