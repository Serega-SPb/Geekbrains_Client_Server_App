import json

ENCODING = 'utf-8'
BUFFER = 512


def send_request(socket, request):
    request_dict = request.get_dict()
    js_str = json.dumps(request_dict)
    socket.send(js_str.encode(ENCODING))


def get_data(socket):
    response = socket.recv(BUFFER)
    if not isinstance(response, bytes):
        raise ValueError
    response_data = json.loads(response.decode(ENCODING))
    return response_data
