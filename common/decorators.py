import json
from jim.codes import SERVER_ERROR, SERVER_UNAVAILABLE, INCORRECT_REQUEST


def try_except_wrapper(func):
    """ For class methods with a logger """
    def wrapper(*args, **kwargs):
        logger = args[0].logger
        try:
            return func(*args, **kwargs)
        except (json.JSONDecodeError, ValueError) as e:
            logger.critical(INCORRECT_REQUEST)
            logger.critical(e)
        except ConnectionRefusedError:
            logger.error(SERVER_UNAVAILABLE)
        except ConnectionError:
            logger.error(SERVER_ERROR)
        except Exception as ex:
            logger.error(ex)
        return None
    return wrapper


def transaction(func):
    """ For database class methods with a logger """
    def wrapper(*args, **kwargs):
        session = args[0].session
        logger = args[0].logger
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            session.rollback()
            logger.error(e)
            return False
        else:
            session.commit()
            return res
    return wrapper
