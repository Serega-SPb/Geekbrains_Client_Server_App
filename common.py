import json

from jim.constants import *


def wrapper(logger, f, *args):
    try:
        return f(*args)
    except (json.JSONDecodeError, ValueError):
        logger.critical(INCORRECT_REQUEST)
    except ConnectionError:
        logger.error(SERVER_ERROR)
    return None


# from datetime import datetime as dt
# def print_error(error):
#     print_log(f'ERROR: {error}')
#
#
# def print_log(message):
#     print(f'{dt.now().strftime("%d/%m/%y %H:%M:%S")} | {message}')
