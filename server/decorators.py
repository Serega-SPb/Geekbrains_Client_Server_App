""" The module contains decorators """

import json
from jim.codes import SERVER_ERROR, SERVER_UNAVAILABLE, INCORRECT_REQUEST


def try_except_wrapper(func):
    """ Decorator of try except block
        Using only for methods of class with a logger"""

    def wrapper(*args, **kwargs):
        logger = args[0].logger
        try:
            return func(*args, **kwargs)
        except (json.JSONDecodeError, ValueError) as ex:
            logger.critical(INCORRECT_REQUEST)
            logger.critical(ex)
        except ConnectionRefusedError:
            logger.error(SERVER_UNAVAILABLE)
        except ConnectionError:
            logger.error(SERVER_ERROR)
        except Exception as ex:
            logger.error(ex)
        return None
    return wrapper


def transaction(func):
    """ Decorator of database transaction
        Using only for methods of class with a logger and a db session"""

    def wrapper(*args, **kwargs):
        session = args[0].session
        logger = args[0].logger
        try:
            res = func(*args, **kwargs)
        except Exception as ex:
            session.rollback()
            logger.error(ex)
            return False
        else:
            session.commit()
            return res
    return wrapper
