""" Module start server application """

import argparse
import os
import sys

import yaml
from PyQt5.QtWidgets import QApplication

from server_core import Server
from server_db import ServerStorage
from ui.server_ui_logic import ConfigWindow, MainWindow


def load_config():
    file = os.path.join(ConfigWindow.DIR, ConfigWindow.CONFIG)
    if not os.path.isfile(file):
        return
    with open(file, 'r', encoding='utf-8') as file:
        content = yaml.load(file, yaml.FullLoader)
    return content


def main():

    config = load_config()

    port = config['port'] if config and 'port' in config else 7777
    bind = config['bind'] if config and 'bind' in config else ''
    db_file = config['database'] \
        if config and 'database' in config \
        else 'server_db.db'

    ServerStorage(db_file)

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=port, type=int, nargs='?',
                        help='Port [default=7777]')
    parser.add_argument('-a', '--addr', default=bind, type=str, nargs='?',
                        help='Bind address')

    args = parser.parse_args()
    addr = args.addr
    port = args.port

    server = Server(addr, port)
    server.start()

    application = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    application.exec_()


if __name__ == '__main__':
    main()
