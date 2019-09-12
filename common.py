import json
from datetime import datetime as dt
from jim.constants import *


def wrapper(f, *args):
    try:
        return f(*args)
    except (json.JSONDecodeError, ValueError):
        print_error(INCORRECT_REQUEST)
    except ConnectionError:
        print_error(SERVER_ERROR)
    return None


def print_error(error):
    print_log(f'ERROR: {error}')


def print_log(message):
    print(f'{dt.now().strftime("%d/%m/%y %H:%M:%S")} | {message}')
