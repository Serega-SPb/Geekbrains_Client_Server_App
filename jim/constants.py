from jim.classes import Code

# 1xx
BASIC = Code(100, 'Basic message')
# 2xx
OK = Code(200, 'OK')
CREATED = Code(201, 'Connection created')
# 4xx
INCORRECT_REQUEST = Code(400, 'Incorrect request / json')
CONFLICT = Code(409, 'User already connected')
# 5xx
SERVER_ERROR = Code(500, 'Server error')


class RequestAction:
    PRESENCE = 'presence'
    MESSAGE = 'msg'
    QUIT = 'quit'



