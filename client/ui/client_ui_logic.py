import datetime
import os
import re
import sys


from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QStandardItemModel, QStandardItem


UI_DIR = os.path.dirname(__file__)


class UserWidget(QWidget):
    def __init__(self, username, action_name, action, parent=None):
        super().__init__(parent)
        self.ui()
        self.userLbl.setText(username)
        self.username = username
        self.actinBtn.setText(action_name)
        self.actinBtn.clicked.connect(action)

    def ui(self):
        # self.resize(200, 50)
        box = QHBoxLayout(self)
        self.setLayout(box)

        self.userLbl = QLabel(self)
        self.actinBtn = QPushButton(self)
        self.actinBtn.setFixedSize(50, 25)

        box.addWidget(self.userLbl)
        box.addWidget(self.actinBtn)


class Message(QWidget):
    def __init__(self, user, text, time, parent=None):
        super().__init__(parent)
        self.ui()

        self.userLbl.setText(user)
        self.timeLbl.setText(time)
        self.msgLbl.setText(text)

    def ui(self):
        # self.setGeometry(0, 0, 100, 50)
        # self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        # self.setMaximumWidth(100)

        # self.setStyleSheet('border:1px solid rgb(0, 0, 0);')

        grid = QGridLayout(self)
        self.setLayout(grid)

        self.userLbl = QLabel(self)
        self.timeLbl = QLabel(self)
        self.msgLbl = QLabel(self)

        self.timeLbl.setAlignment(Qt.AlignRight)

        grid.addWidget(self.userLbl, 0, 0)
        grid.addWidget(self.timeLbl, 0, 1)
        grid.addWidget(self.msgLbl, 1, 0, 1, 2)


class LoginWindow(QDialog):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        uic.loadUi(os.path.join(UI_DIR, 'login.ui'), self)
        self.start = False

        self.loginBtn.setEnabled(False)
        self.usernameTxb.textChanged.connect(self.username_text_changed)
        self.loginBtn.clicked.connect(self.login)
        self.exitBtn.clicked.connect(self.close)

    @property
    def username(self):
        return self.usernameTxb.text()

    def username_text_changed(self):
        if len(self.username) > 2:
            self.loginBtn.setEnabled(True)
        else:
            self.loginBtn.setEnabled(False)

    def login(self):
        self.start = True
        self.close()


class SignalStorage(QObject):

    user_connected = pyqtSignal(str)
    user_disconnected = pyqtSignal(str)

    contact_added = pyqtSignal(str)
    contact_removed = pyqtSignal(str)

    got_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)


class MainWindow(QMainWindow):

    SELF_SIDE = 0
    OTHER_SIDE = 1

    def __init__(self, client, parent=None):
        QWidget.__init__(self, parent)
        self.client = client
        self.setWindowTitle(self.client.username)
        self.curr_chat_user = None
        uic.loadUi(os.path.join(UI_DIR, 'client.ui'), self)
        self.init_ui()

    def init_ui(self):
        self.storage = SignalStorage()
        self.set_chat_active(False)

        self.load_users()
        self.load_contacts()

        self.usersList.doubleClicked.connect(self.load_chat)
        self.contactsList.doubleClicked.connect(self.load_chat)
        self.sendMsgBtn.clicked.connect(self.send_message)

        self.storage.user_connected.connect(self.add_online_user)
        self.storage.user_disconnected.connect(self.rem_online_user)
        self.storage.got_message.connect(self.recieve_message)

        self.client.subscribe(201, self.storage.user_connected.emit)
        self.client.subscribe(202, self.storage.user_disconnected.emit)
        self.client.subscribe(203, self.storage.got_message.emit)

    @property
    def message(self):
        return self.messageTxa.toPlainText()

    @message.setter
    def message(self, value):
        self.messageTxa.setText(value)

    @staticmethod
    def __add_user_in_list(list_view, user, action_name, action):
        item = QListWidgetItem()
        item.user = user
        widget = UserWidget(user, action_name, action, list_view)
        widget.setObjectName(user)

        item.setSizeHint(widget.sizeHint())
        list_view.addItem(item)
        list_view.setItemWidget(item, widget)

    @staticmethod
    def __rem_user_from_list(list_view, user):
        items = [list_view.item(i) for i in range(list_view.count())]
        item = [i for i in items if hasattr(i, 'user') and i.user == user]
        if len(item) > 0:
            list_view.takeItem(list_view.row(item[0]))

    def load_users(self):
        self.client.get_users_req()
        users = self.client.answers.get()
        for u in users:
            if u == self.client.username:
                continue
            self.add_online_user(u)

    def add_online_user(self, user):
        self.__add_user_in_list(self.usersList, user, 'Add', self.add_contact)

    def rem_online_user(self, user):
        self.__rem_user_from_list(self.usersList, user)

    def load_contacts(self):
        self.client.get_contacts_req()
        contacts = self.client.answers.get()
        self.client.sync_contacts(contacts)
        for c in contacts:
            self.__add_user_in_list(self.contactsList, c, 'Del', self.remove_contact)

    def add_contact(self):
        sender = self.sender()
        widget = sender.parent()
        username = widget.username
        r = self.client.add_contact(username)
        if r == False:
            return
        self.client.answers.get()
        self.__add_user_in_list(self.contactsList, username, 'Del', self.remove_contact)

    def remove_contact(self):
        sender = self.sender()
        widget = sender.parent()
        username = widget.username
        self.client.rem_contact(username)
        self.client.answers.get()
        self.__rem_user_from_list(self.contactsList, username)

    def load_chat(self):
        self.chatList.clear()
        sender = self.sender()
        items = sender.selectedItems()
        if len(items) == 0:
            return
        widget = sender.selectedItems()[0]
        username = widget.user
        self.set_chat_active(True)
        self.curr_chat_user = username
        self.client.get_chat_req(self.curr_chat_user)
        chat = self.client.answers.get()
        for msg in chat:
            self.parse_message(msg)

    SENDER = 'sender'
    RECV = 'recv'
    MSG = 'msg'
    recv_pat = rf'^(?P<{SENDER}>[\w\d]*) to @(?P<{RECV}>[\w]*): (?P<{MSG}>.*)'
    TIME_FMT = '%Y-%m-%d %H:%M:%S.%f'

    def recieve_message(self, msg):
        match = re.match(self.recv_pat, msg)
        sender = match.group(self.SENDER)
        recv = match.group(self.RECV)
        msg = match.group(self.MSG)
        time = time = datetime.datetime.now().strftime('%H:%M')  # TODO get from resp
        self.add_message_in_chat(self.OTHER_SIDE, sender, msg, time)

    def parse_message(self, msg):
        sender, time, message, recv = msg.split('__')
        time = datetime.datetime.strptime(time, self.TIME_FMT).strftime('%H:%M')
        side = self.SELF_SIDE if sender == self.client.username else self. OTHER_SIDE
        self.add_message_in_chat(side, sender, message, time)

    def send_message(self):
        user = self.curr_chat_user
        msg = self.message
        time = datetime.datetime.now().strftime('%H:%M')
        self.client.send_msg(msg, user)
        self.add_message_in_chat(self.SELF_SIDE, self.client.username, msg, time)
        self.message = ''

    def add_message_in_chat(self, side, user, msg, time):
        if user not in [self.client.username, self.curr_chat_user]:
            return

        item = QListWidgetItem()
        item.setTextAlignment(Qt.AlignLeft if side == self.SELF_SIDE else Qt.AlignRight)
        widget = Message(user, msg, time)

        item.setSizeHint(widget.sizeHint())
        self.chatList.addItem(item)
        self.chatList.setItemWidget(item, widget)

    def set_chat_active(self, flag):
        self.chatList.setEnabled(flag)
        self.messageTxa.setEnabled(flag)
        self.sendMsgBtn.setEnabled(flag)
