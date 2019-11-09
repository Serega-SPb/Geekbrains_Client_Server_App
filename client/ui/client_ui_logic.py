""" Module implements main window logic """

from datetime import datetime
import os

from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem

from .client_ui import Ui_MainWindow as ClientMainWindow
from .additional_ui import UserWidget, Message, LoginWindow, MessageBox

UI_DIR = os.path.dirname(__file__)


class SignalStorage(QObject):
    """ Class the signal storage """

    user_connected = pyqtSignal(str)
    user_disconnected = pyqtSignal(str)

    contact_added = pyqtSignal(str)
    contact_removed = pyqtSignal(str)

    starting_chat = pyqtSignal(str)
    accepted_chat = pyqtSignal(str)
    got_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)


class MainWindow(QMainWindow):
    """ Class the implementation of main window logic """

    SELF_SIDE = 0
    OTHER_SIDE = 1

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle(self.client.username)
        self.curr_chat_user = None
        # uic.loadUi(os.path.join(UI_DIR, 'client.ui'), self)
        self.ui = ClientMainWindow()
        self.ui.setupUi(self)
        self.init_ui()

    def init_ui(self):
        """ Method the initialization ui and link ui widgets to logic """

        self.storage = SignalStorage()
        self.set_chat_active(False)

        self.load_users()
        self.load_contacts()

        self.ui.usersList.doubleClicked.connect(self.start_chat)
        self.ui.contactsList.doubleClicked.connect(self.start_chat)
        self.ui.sendMsgBtn.clicked.connect(self.send_message)

        self.storage.user_connected.connect(self.add_online_user)
        self.storage.user_disconnected.connect(self.rem_online_user)
        self.storage.got_message.connect(self.recieve_message)

        self.storage.starting_chat.connect(self.starting_chat)
        self.storage.accepted_chat.connect(self.accepted_chat)

        self.client.subscribe(201, self.storage.user_connected.emit)
        self.client.subscribe(202, self.storage.user_disconnected.emit)
        self.client.subscribe(203, self.storage.got_message.emit)
        self.client.subscribe(204, self.storage.starting_chat.emit)
        self.client.subscribe(205, self.storage.accepted_chat.emit)

    @property
    def message(self):
        return self.ui.messageTxa.toPlainText()

    @message.setter
    def message(self, value):
        self.ui.messageTxa.setText(value)

    @staticmethod
    def __add_user_in_list(list_view, user, action_name, action):
        """ Method adds user in list on ui """

        item = QListWidgetItem()
        item.user = user
        widget = UserWidget(user, action_name, action, list_view)
        widget.setObjectName(user)

        item.setSizeHint(widget.sizeHint())
        list_view.addItem(item)
        list_view.setItemWidget(item, widget)

    @staticmethod
    def __rem_user_from_list(list_view, user):
        """ Method removes user from list on ui """

        items = [list_view.item(i) for i in range(list_view.count())]
        item = [i for i in items if hasattr(i, 'user') and i.user == user]
        if len(item) > 0:
            list_view.takeItem(list_view.row(item[0]))

    def __get_collection_response(self):
        result = []
        while True:
            resp = self.client.answers.get()
            if not resp:
                break
            result.append(resp)
        return result

    def load_users(self):
        """ Method loads users in online list """

        self.client.get_users_req()
        # users = self.client.answers.get()
        users = self.__get_collection_response()

        for user in users:
            if user == self.client.username:
                continue
            self.add_online_user(user)

    def add_online_user(self, user):
        """ Method adds user in online list """

        self.__add_user_in_list(self.ui.usersList, user,
                                'Add', self.add_contact)

    def rem_online_user(self, user):
        """ Method removes user in online list """

        self.__rem_user_from_list(self.ui.usersList, user)

    def load_contacts(self):
        """ Method loads users in contact list """

        self.client.get_contacts_req()
        # contacts = self.client.answers.get()
        contacts = self.__get_collection_response()
        self.client.sync_contacts(contacts)
        for contact in contacts:
            self.__add_user_in_list(self.ui.contactsList, contact,
                                    'Del', self.remove_contact)

    def add_contact(self):
        """ Method adds user in contact list """

        sender = self.sender()
        widget = sender.parent()
        username = widget.username
        if not self.client.add_contact(username):
            return
        self.client.answers.get()
        self.__add_user_in_list(self.ui.contactsList, username,
                                'Del', self.remove_contact)

    def remove_contact(self):
        """ Method removes user in contact list """

        sender = self.sender()
        widget = sender.parent()
        username = widget.username
        self.client.rem_contact(username)
        self.client.answers.get()
        self.__rem_user_from_list(self.ui.contactsList, username)

    def start_chat(self):
        """ Method the initialization chat with user """

        self.ui.chatList.clear()
        sender = self.sender()
        items = sender.selectedItems()
        if len(items) == 0:
            return
        widget = sender.selectedItems()[0]
        username = widget.user
        self.curr_chat_user = username
        if self.client.start_chat(username) is True:
            self.load_chat()

    def starting_chat(self, resp):
        """ Method the handler of request of start chat """

        # self.curr_chat_user =
        self.client.accepting_chat(resp)
        # self.load_chat()

    def accepted_chat(self, resp):
        """ Method the handler of request of initialized chat """

        self.client.accepted_chat(resp)
        self.load_chat()

    def load_chat(self):
        """ Method the load chat messages on ui """

        self.set_chat_active(True)
        self.client.get_chat_req(self.curr_chat_user)
        # chat = self.client.answers.get()
        chat = self.__get_collection_response()
        for msg in chat:
            self.parse_message(msg)

    TIME_FMT = '%Y-%m-%d %H:%M:%S.%f'

    def recieve_message(self, msg):
        """ Method of handle of received message """

        sender, msg = self.client.parse_recv_message(msg)
        # TODO get from resp
        time = time = datetime.now().strftime('%H:%M')
        self.add_message_in_chat(self.OTHER_SIDE, sender, msg, time)

    def parse_message(self, msg):
        """ Method the parse chat messages gotten from server """
        # TODO not UI logic

        sender, time, message, _ = msg.split('__')
        time = datetime.strptime(time, self.TIME_FMT).strftime('%H:%M')
        side = self.SELF_SIDE \
            if sender == self.client.username \
            else self.OTHER_SIDE
        message = self.client.get_encryptor(self.curr_chat_user)\
                             .decrypt_msg(message).decode()
        self.add_message_in_chat(side, sender, message, time)

    def send_message(self):
        """ Method the send message in chat """

        user = self.curr_chat_user
        msg = self.message
        time = datetime.now().strftime('%H:%M')
        self.client.send_msg(msg, user)
        self.add_message_in_chat(self.SELF_SIDE,
                                 self.client.username, msg, time)
        self.message = ''

    def add_message_in_chat(self, side, user, msg, time):
        """ Method the add message in chat """

        if user not in [self.client.username, self.curr_chat_user]:
            return

        item = QListWidgetItem()
        item.setTextAlignment(Qt.AlignLeft
                              if side == self.SELF_SIDE
                              else Qt.AlignRight)
        widget = Message(user, msg, time)

        item.setSizeHint(widget.sizeHint())
        self.ui.chatList.addItem(item)
        self.ui.chatList.setItemWidget(item, widget)

    def set_chat_active(self, flag):
        """ Method set active of chat widgets """

        self.ui.chatList.setEnabled(flag)
        self.ui.messageTxa.setEnabled(flag)
        self.ui.sendMsgBtn.setEnabled(flag)
