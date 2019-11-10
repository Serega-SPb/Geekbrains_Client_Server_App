""" Module start client application """

import argparse
import os
import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from client_core import Client
from ui.additional_ui import LoginWindow
from ui.client_ui_logic import MainWindow


def show_error(mes):
    #msb = MessageBox(mes)
    msb = QMessageBox()
    msb.setWindowTitle('Error')
    msb.setText(mes)
    msb.show()
    msb.exec_()


USER_DATA_DIR = 'user_data'


def preparing():
    if not os.path.exists(USER_DATA_DIR):
        os.mkdir(USER_DATA_DIR)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default='localhost', type=str, nargs='?',
                        help='Server address [default=localhost]')
    parser.add_argument('port', default=7777, type=int, nargs='?',
                        help='Server port [default=7777]')

    args = parser.parse_args()

    addr = args.addr
    port = args.port

    preparing()
    app = QApplication(sys.argv)
    login = LoginWindow()

    login.ip = addr
    login.port = port

    login.show()
    app.exec_()

    if not login.start:
        return
    login.close()

    client = Client(login.ip, login.port)
    client.set_user(login.username, login.password)
    client.start()
    if not client.connected:
        show_error('Service Unavailable')
        exit()

    win = MainWindow(client)
    win.setWindowTitle(client.username)
    win.show()
    app.exec_()


if __name__ == '__main__':
    main()
