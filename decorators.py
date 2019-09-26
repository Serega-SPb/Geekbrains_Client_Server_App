import json
from jim.constants import *


def log_call_method(func):
    def wrapper(*args, **kwargs):
        logger = args[0].logger
        logger.debug(f'Func {func.__name__} with args {args}, {kwargs} is called from {func.__module__} ')
        return func(*args, **kwargs)
    return wrapper


def try_except_wrapper(func):
    """ For class methods with a logger """
    def wrapper(*args, **kwargs):
        logger = args[0].logger
        try:
            return func(*args, **kwargs)
        except (json.JSONDecodeError, ValueError):
            logger.critical(INCORRECT_REQUEST)
        except ConnectionError:
            logger.error(SERVER_ERROR)
        except Exception as ex:
            logger.error(ex)
        return None
    return wrapper
