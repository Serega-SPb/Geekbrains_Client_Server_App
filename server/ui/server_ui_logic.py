""" Module implements ui logic and addinional widgets """

import logging
import os
import sys
from threading import Lock

import yaml

from PyQt5.QtCore import QTimer, QMetaObject, Qt, Q_ARG
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, \
                            QDialog, QFileDialog, QLineEdit, QRadioButton
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from logs import server_log_config as log_config
from server_db import ServerStorage
from .server_ui import Ui_MainWindow as ServerMainWindow
from .server_config_ui import Ui_Dialog as ConfigDialog


UI_DIR = os.path.dirname(__file__)


def add_row(model, row_ind, source, cols_field):
    """ Function adds row in table in ui """

    col_ind = 0
    for f in cols_field:
        data = source
        path = f.split('.')
        for p in path:
            if not p:
                continue
            if p.startswith('['):
                key = p[1:-1]
                if key.isdigit():
                    data = data[int(key)]
                else:
                    data = data[key]
            else:
                data = getattr(data, p)

        item = QStandardItem(str(data))
        item.setEditable(False)
        model.setItem(row_ind, col_ind, item)
        col_ind += 1


def fill_table(table, data, headers, fields):
    """ Function fills table in ui """

    model = QStandardItemModel(len(data), len(headers))
    model.setHorizontalHeaderLabels(headers)
    for i, d in enumerate(data):
        add_row(model, i, d, fields)
    table.setModel(model)


class UiLogHandler(logging.Handler):
    """ Class the log handler """

    def __init__(self, log_widget):
        super().__init__()
        self.widget = log_widget
        self.widget.setReadOnly(True)
        self.setFormatter(log_config.server_formatter)
        self.setLevel(log_config.STREAM_LOG_LVL)
        self.locker = Lock()

    def emit(self, record):
        with self.locker:
            QMetaObject.invokeMethod(self.widget, "appendPlainText",
                                     Qt.QueuedConnection,
                                     Q_ARG(str, self.format(record)))


class ConfigWindow(QDialog):
    """ Class the config dialog logic """

    DIR = os.getcwd()
    CONFIG = 'server.cfg'

    IS_MONGO_DB = 'is_mongo_db'
    DB_HOST = 'db_host'
    IS_SQLITE_DB = 'is_sqlite_db'
    DB_FILE = 'database'
    PORT = 'port'
    BIND_ADDR = 'bind'

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        # uic.loadUi(os.path.join(UI_DIR, 'server_config.ui'), self)
        self.ui = ConfigDialog()
        self.ui.setupUi(self)
        self.fields = {
            self.IS_MONGO_DB: self.ui.mongo_db_rbn,
            self.DB_HOST: self.ui.db_host_txb,
            self.IS_SQLITE_DB: self.ui.sqlite_db_rbn,
            self.DB_FILE: self.ui.db_filepath_txb,
            self.PORT: self.ui.port_txb,
            self.BIND_ADDR: self.ui.bind_addr_txb
        }
        self.__init_ui()
        self.load_confg()

    def save_config(self):
        """ Method save config """

        data = {}
        for p, f in self.fields.items():
            if isinstance(f, QLineEdit):
                data[p] = f.text()
            elif isinstance(f, QRadioButton):
                data[p] = f.isChecked()

        file = os.path.join(self.DIR, self.CONFIG)
        with open(file, 'w', encoding='utf-8') as file:
            yaml.dump(data, file)

    def load_confg(self):
        """ Method load config """

        file = os.path.join(self.DIR, self.CONFIG)
        if not os.path.isfile(file):
            return
        with open(file, 'r', encoding='utf-8') as file:
            content = yaml.load(file, yaml.FullLoader)
        for k, v in content.items():
            if k in self.fields:
                wid = self.fields[k]
                if isinstance(wid, QLineEdit):
                    wid.setText(v)
                elif isinstance(wid, QRadioButton):
                    wid.setChecked(v)

    def __init_ui(self):
        """ Method the initialization ui and link ui widgets to logic """

        def open_file_dialog():
            """ Function of opens file dialog """

            dialog = QFileDialog(self)
            path = dialog.getOpenFileName()[0]
            path = os.path.relpath(path, os.getcwd())
            self.ui.db_filepath_txb.setText(path)
            print(path)

        def save_btn_click():
            """ Function the handler save button click event """

            self.save_config()
            QMessageBox.information(self, 'Info', 'Restart the program to apply the changes')
            self.close()

        self.ui.select_file_btn.clicked.connect(lambda: open_file_dialog())
        self.ui.save_btn.clicked.connect(lambda: save_btn_click())
        self.ui.cancel_btn.clicked.connect(lambda: self.close())


class MainWindow(QMainWindow):
    """ Class the implementation of main window logic """

    def __init__(self, storage=None, parent=None):
        QWidget.__init__(self, parent)
        # uic.loadUi(os.path.join(UI_DIR, 'server.ui'), self)
        self.ui = ServerMainWindow()
        self.ui.setupUi(self)
        logging.getLogger(log_config.LOGGER_NAME)\
            .addHandler(UiLogHandler(self.ui.logPtx))
        self.storage = storage if storage else ServerStorage()
        self.__init_ui()

    def __init_ui(self):
        """ Method the initialization ui and link ui widgets to logic """

        def switch_refresh():
            """ Function the handler of refresh action """

            if self.ui.action_refresh.isChecked():
                self.timer_refresh.start()
            else:
                self.timer_refresh.stop()

        def open_config_func():
            """ Function of opens config dialog """

            win = ConfigWindow(self)
            win.exec_()

        self.ui.open_config.triggered.connect(lambda: open_config_func())
        self.ui.action_refresh.triggered.connect(lambda: switch_refresh())
        self.refresh()

        self.timer_refresh = QTimer()
        self.timer_refresh.setInterval(10000)
        self.timer_refresh.timeout.connect(self.refresh)

        self.ui.action_refresh.trigger()

    def refresh(self):
        """ Method the reload all tables """

        self.load_users()
        self.load_users_online()
        # self.load_users_stats()
        self.load_history()
        self.load_messages()
        self.load_avatars()

    def load_users(self):
        """ Method the load users table"""

        users = self.storage.get_users()  # temp
        tbl = self.ui.users_tbl
        fill_table(tbl, users, ['id', 'name', 'password'], ['id', 'name', 'password'])

    def load_users_online(self):
        """ Method the load online users table"""

        online = self.storage.get_users_online()
        tbl = self.ui.users_online_tbl
        fields = ['name'] \
            if isinstance(self.storage, ServerStorage) \
            else ['.']
        fill_table(tbl, online, ['name'], fields)

    # def load_users_stats(self):
    #     """ Method the load users stats table"""
    #
    #     stats = self.storage.get_user_stats()
    #     tbl = self.ui.user_stats_tbl
    #     fields = ['User.name', 'UserStat.mes_sent', 'UserStat.mes_recv'] \
    #         if isinstance(self.storage, ServerStorage) \
    #         else ['id', 'name', 'password']
    #     fill_table(tbl, stats, ['name', 'sent', 'recv'], fields)

    def load_history(self):
        """ Method the load history table"""

        history = self.storage.get_history()
        tbl = self.ui.history_tbl
        fields = ['LoginHistory.id', 'User.name',
                  'LoginHistory.datetime', 'LoginHistory.ip'] \
            if isinstance(self.storage, ServerStorage) \
            else ['[0].id', '[0].name', '[1].datetime', '[1].ip']
        fill_table(tbl, history, ['id', 'name', 'date', 'ip'], fields)

    def load_messages(self):
        """ Method the load users messages table"""

        messages = self.storage.get_user_messages()
        tbl = self.ui.messages_tbl
        fields = ['UserMessage.id', '[0].name', '[2].name',
                  'UserMessage.text', 'UserMessage.time'] \
            if isinstance(self.storage, ServerStorage) \
            else ['id', 'sender.name', 'recipient.name', 'text', 'time']
        fill_table(tbl, messages,
                   ['id', 'sender', 'recipient', 'text', 'time'], fields)

    def load_avatars(self):

        avatars = self.storage.get_users_avatar()
        tbl = self.ui.avatars_tbl
        fields = ['User.name', 'UserAvatar.avatar_hash', 'UserAvatar.avatar'] \
            if isinstance(self.storage, ServerStorage) \
            else ['name', 'avatar_hash', 'avatar']
        fill_table(tbl, avatars, ['user', 'avatar_md5', 'avatar'], fields)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
