import logging
import os
import sys
from threading import Lock

import yaml

from PyQt5 import uic
from PyQt5.QtCore import QTimer, QMetaObject, Qt, Q_ARG
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QStandardItemModel, QStandardItem

import logs.server_log_config as log_config
from server_db import ServerStorage


UI_DIR = os.path.dirname(__file__)


def add_row(model, row_ind, source, cols_field):
    col_ind = 0
    for f in cols_field:
        path = f.split('.')
        data = source
        for p in path:
            if p.startswith('['):
                data = data[int(p[1:-1])]
            else:
                data = getattr(data, p)

        item = QStandardItem(str(data))
        item.setEditable(False)
        model.setItem(row_ind, col_ind, item)
        col_ind += 1


def fill_table(table, data, headers, fields):
    model = QStandardItemModel(len(data), len(headers))
    model.setHorizontalHeaderLabels(headers)
    for i, d in enumerate(data):
        add_row(model, i, d, fields)
    table.setModel(model)


class UiLogHandler(logging.Handler):
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
                                     Qt.QueuedConnection, Q_ARG(str, self.format(record)))


class ConfigWindow(QDialog):

    DIR = os.getcwd()
    CONFIG = 'server.cfg'

    DB_FILE = 'database'
    PORT = 'port'
    BIND_ADDR = 'bind'

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        uic.loadUi(os.path.join(UI_DIR, 'server_config.ui'), self)
        self.fields = {
            self.DB_FILE: self.db_filepath_txb,
            self.PORT: self.port_txb,
            self.BIND_ADDR: self.bind_addr_txb
        }
        self.__init_ui()
        self.load_confg()

    def save_config(self):
        d = {p: f.text() for p, f in self.fields.items()}
        with open(os.path.join(self.DIR, self.CONFIG), 'w', encoding='utf-8') as file:
            yaml.dump(d, file)

    def load_confg(self):
        file = os.path.join(self.DIR, self.CONFIG)
        if not os.path.isfile(file):
            return
        with open(file, 'r', encoding='utf-8') as file:
            content = yaml.load(file, yaml.FullLoader)
        for k, v in content.items():
            if k in self.fields:
                self.fields[k].setText(v)

    def __init_ui(self):

        def open_file_dialog():
            dialog = QFileDialog(self)
            path = dialog.getOpenFileName()[0]
            path = os.path.relpath(path, os.getcwd())
            self.db_filepath_txb.setText(path)
            print(path)

        def save_btn_click():
            self.save_config()
            self.close()

        self.select_file_btn.clicked.connect(lambda: open_file_dialog())
        self.save_btn.clicked.connect(lambda: save_btn_click())
        self.cancel_btn.clicked.connect(lambda: self.close())


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        uic.loadUi(os.path.join(UI_DIR, 'server.ui'), self)
        logging.getLogger(log_config.LOGGER_NAME).addHandler(UiLogHandler(self.logPtx))
        self.storage = ServerStorage()
        self.__init_ui()

    def __init_ui(self):

        def switch_refresh():
            if self.action_refresh.isChecked():
                self.timer_refresh.start()
            else:
                self.timer_refresh.stop()

        def open_config_func():
            win = ConfigWindow(self)
            win.exec_()

        self.open_config.triggered.connect(lambda: open_config_func())
        self.action_refresh.triggered.connect(lambda: switch_refresh())
        self.refresh()

        self.timer_refresh = QTimer()
        self.timer_refresh.setInterval(10000)
        self.timer_refresh.timeout.connect(self.refresh)

        self.action_refresh.trigger()

    def refresh(self):
        self.load_users()
        self.load_users_online()
        self.load_users_stats()
        self.load_history()
        self.load_messages()

    def load_users(self):
        users = self.storage.get_users()  # temp
        tbl = self.users_tbl
        fill_table(tbl, users, ['id', 'name'], ['id', 'name'])

    def load_users_online(self):
        online = self.storage.get_users_online()
        tbl = self.users_online_tbl
        fill_table(tbl, online, ['name'], ['name'])

    def load_users_stats(self):
        stats = self.storage.get_user_stats()
        tbl = self.user_stats_tbl
        fill_table(tbl, stats, ['name', 'sent', 'recv'], ['User.name', 'UserStat.mes_sent', 'UserStat.mes_recv'])

    def load_history(self):
        history = self.storage.get_history()
        tbl = self.history_tbl
        fill_table(tbl, history, ['id', 'name', 'date', 'ip'],
                   ['LoginHistory.id', 'User.name', 'LoginHistory.datetime', 'LoginHistory.ip'])

    def load_messages(self):
        messages = self.storage.get_user_messages()
        tbl = self.messages_tbl
        fill_table(tbl, messages, ['id', 'sender', 'recipient', 'text', 'time'],
                   ['UserMessage.id', '[0].name', '[2].name', 'UserMessage.text', 'UserMessage.time'])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
