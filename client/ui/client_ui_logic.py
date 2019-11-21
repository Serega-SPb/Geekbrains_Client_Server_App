""" Module implements main window logic """

from base64 import b64encode, b64decode
from datetime import datetime
import os

from PyQt5.QtCore import Qt, pyqtSignal, QObject, QBuffer, QIODevice, QByteArray
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem, QMessageBox, QFrame

from .client_ui import Ui_MainWindow as ClientMainWindow
from .additional_ui import UserWidget, MessageWidget, LoginWindow, ImageFilterWidnow

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
        self.avatars = {}
        self.user_widgets = {}
        self.setWindowTitle(self.client.username)
        self._curr_chat_user = None
        # uic.loadUi(os.path.join(UI_DIR, 'client.ui'), self)
        self.ui = ClientMainWindow()
        self.ui.setupUi(self)
        self.init_ui()

    def init_ui(self):
        """ Method the initialization ui and link ui widgets to logic """

        self.storage = SignalStorage()
        # self.set_chat_active(False)
        self.curr_chat_user = '@ALL'
        self.load_chat()

        self.load_avatar()
        self.load_users()
        self.load_contacts()

        self.ui.addContactTbx.textChanged.connect(
            lambda x: self.ui.addContactBtn.setEnabled(len(x) > 2))
        self.ui.addContactBtn.clicked.connect(
            lambda: self.add_contact_by_name(self.ui.addContactTbx.text()))

        def close_chat():
            self.curr_chat_user = '@ALL'
            self.load_chat()

        self.ui.closeChatBtn.clicked.connect(close_chat)

        self.ui.avatarLbl.mouseDoubleClickEvent = self.set_avatar
        self.ui.usernameLbl.setText(self.client.username)

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

    @property
    def curr_chat_user(self):
        return self._curr_chat_user

    @curr_chat_user.setter
    def curr_chat_user(self, value):
        self._curr_chat_user = value
        self.ui.chatNameLbl.setText(value)
        self.ui.closeChatBtn.setEnabled(not value.startswith('@'))

    def set_avatar(self, *args, **kwargs):
        image_filter_win = ImageFilterWidnow(self)
        image_filter_win.setModal(True)
        image_filter_win.exec_()

        answer = QMessageBox.question(self, 'Question', 'Use this image',
                                      QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.No:
            return
        buf = QBuffer()
        buf.open(QIODevice.ReadWrite)
        image_filter_win.save_file(buf, 48)
        data = buf.data().data()
        self.client.avatar = data
        self.__load_avatar(data)

    def __load_avatar(self, avatar_bytes):
        img = QImage.fromData(avatar_bytes)
        self.ui.avatarLbl.setPixmap(QPixmap.fromImage(img))
        self.ui.avatarLbl.setFrameShape(QFrame.NoFrame)

    def load_avatar(self):
        avatar = self.client.avatar
        if avatar:
            self.__load_avatar(avatar)
            self.client.check_self_avatar()

    @staticmethod
    def __add_user_in_list(list_view, user, action_name, action, avatar):
        """ Method adds user in list on ui """

        item = QListWidgetItem()
        item.user = user
        widget = UserWidget(user, avatar, action_name, action, list_view)
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

    def __get_user_avatar(self, user):
        if user not in self.avatars.keys():
            avatar = self.client.get_user_avatar(user)
            self.avatars[user] = avatar
        else:
            avatar = self.avatars[user]
        return avatar

    def load_users(self):
        """ Method loads users in online list """

        self.client.get_users_req()
        users = self.client.get_collection_response()
        # users = self.client.answers.get()
        # users = self.__get_collection_response()

        for user in users:
            if user == self.client.username:
                continue
            self.add_online_user(user)

    def add_online_user(self, user):
        """ Method adds user in online list """

        self.__add_user_in_list(self.ui.usersList, user,
                                'Add', self.add_contact,
                                self.__get_user_avatar(user))

    def rem_online_user(self, user):
        """ Method removes user in online list """

        self.__rem_user_from_list(self.ui.usersList, user)

    def load_contacts(self):
        """ Method loads users in contact list """

        self.client.get_contacts_req()
        contacts = self.client.get_collection_response()
        # contacts = self.client.answers.get()
        # contacts = self.__get_collection_response()

        self.client.sync_contacts(contacts)
        for contact in contacts:
            self.__add_user_in_list(self.ui.contactsList, contact,
                                    'Del', self.remove_contact,
                                    self.__get_user_avatar(contact))

    def add_contact(self):
        """ Method adds user in contact list """

        sender = self.sender()
        widget = sender.parent()
        username = widget.username
        self.add_contact_by_name(username)
        # if not self.client.add_contact(username):
        #     return
        # self.client.answers.get()
        # self.__add_user_in_list(self.ui.contactsList, username,
        #                         'Del', self.remove_contact,
        #                         self.__get_user_avatar(username))

    def add_contact_by_name(self, username):
        self.ui.addContactTbx.clear()
        if not self.client.add_contact(username):
            return

        # TODO temp
        try:
            self.client.answers.get(timeout=2)
        except Exception as e:
            self.client.logger.error(e)
        else:
            self.__add_user_in_list(self.ui.contactsList, username,
                                    'Del', self.remove_contact,
                                    self.__get_user_avatar(username))

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

        self.ui.chatList.clear()
        self.set_chat_active(True)
        self.client.get_chat_req(self.curr_chat_user)
        chat = self.client.get_collection_response()
        # chat = self.client.answers.get()
        # chat = self.__get_collection_response()
        if chat:
            for msg in chat:
                self.parse_message(msg)

    TIME_FMT = '%Y-%m-%d %H:%M:%S.%f'

    def recieve_message(self, msg):
        """ Method of handle of received message """

        sender, msg = self.client.parse_recv_message(msg)
        # TODO get from resp
        time = datetime.now().strftime('%H:%M')
        self.add_message_in_chat(self.OTHER_SIDE, sender, msg, time)

    def parse_message(self, msg):
        """ Method the parse chat messages gotten from server """
        # TODO not UI logic

        sender, time, message, *_ = msg.split('__')
        time = datetime.strptime(time, self.TIME_FMT).strftime('%H:%M')
        side = self.SELF_SIDE \
            if sender == self.client.username \
            else self.OTHER_SIDE
        if self.curr_chat_user != '@ALL':
            message = self.client.get_encryptor(self.curr_chat_user)\
                             .decrypt_msg(message).decode()
        else:
            message = b64decode(message).decode()
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

        if self.curr_chat_user != '@ALL' and \
                user not in [self.client.username, self.curr_chat_user]:
            return
        item = QListWidgetItem()
        item.setTextAlignment(Qt.AlignLeft
                              if side == self.SELF_SIDE
                              else Qt.AlignRight)
        widget = MessageWidget(user, msg, time)

        item.setSizeHint(widget.sizeHint())
        self.ui.chatList.addItem(item)
        self.ui.chatList.setItemWidget(item, widget)
        self.ui.chatList.scrollToBottom()

    def set_chat_active(self, flag):
        """ Method set active of chat widgets """

        self.ui.chatList.setEnabled(flag)
        self.ui.messageTxa.setEnabled(flag)
        self.ui.sendMsgBtn.setEnabled(flag)
