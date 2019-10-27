import logging
import os
import sys

LOGGER_NAME = 'client'

LOGGING_LVL = logging.DEBUG
FILE_LOG_LVL = logging.WARNING
STREAM_LOG_LVL = logging.INFO

LOG_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LOG_FILENAME = f'{LOGGER_NAME}.log'
ENCODING = 'utf-8'

client_formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(module)s | %(message)s')

stream_hnd = logging.StreamHandler(sys.stdout)
stream_hnd.setFormatter(client_formatter)
stream_hnd.setLevel(STREAM_LOG_LVL)

file_hnd = logging.FileHandler(os.path.join(LOG_DIRECTORY, LOG_FILENAME), encoding=ENCODING)
file_hnd.setFormatter(client_formatter)
file_hnd.setLevel(FILE_LOG_LVL)

logger = logging.getLogger(LOGGER_NAME)
logger.addHandler(stream_hnd)
logger.addHandler(file_hnd)
logger.setLevel(LOGGING_LVL)

if __name__ == '__main__':
    logger.critical('Test critical event')
    logger.error('Test error event')
    logger.warning('Test warning event')
    logger.debug('Test debug event')
    logger.info('Test info event')
