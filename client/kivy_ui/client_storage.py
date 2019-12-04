import logging
from base64 import b64decode

from client_core import Client
from decorators import try_except_wrapper
from logs import client_log_config as log_config
from metaclasses import Singleton


class Event:
    def __init__(self, *arg_types):
        self.subscribers = []
        self.arg_types = arg_types

    def __iadd__(self, func):
        self.subscribers.append(func)
        return self

    def __isub__(self, func):
        self.subscribers.remove(func)
        return self

    def emit(self, *args):
        [sub(*args) for sub in self.subscribers]


class ClientAppStorage(metaclass=Singleton):

    # region Events

    # ?ip-addr:port?
    username_changed = Event(str)
    avatar_changed = Event(bytes)

    users_loaded = Event(list)
    contacts_loaded = Event(list)
    messages_loaded = Event(list)

    user_connected = Event(str)
    user_disconnected = Event(str)
    contact_added = Event(str)
    contact_removed = Event(str)

    got_message = Event(str)
    starting_chat_ev = Event(str)
    accepted_chat_ev = Event(str)

    image_selected = Event(str)
    # endregion

    def __init__(self):
        self.client = None
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        self.avatars = {}
        self.curr_chat_user = None

    def init_client(self, addr, port, username, passwod):
        self.client = Client(addr, port)
        self.client.set_user(username, passwod)
        self.username_changed.emit(username)

        self.client.subscribe(201, self.user_connected.emit)
        self.client.subscribe(202, self.user_disconnected.emit)
        self.client.subscribe(203, self.got_message.emit)
        self.client.subscribe(204, self.starting_chat_ev.emit)
        self.client.subscribe(205, self.accepted_chat_ev.emit)

        self.starting_chat_ev += self.client.accepting_chat
        self.accepted_chat_ev += self.accepted_chat

    def start_client(self):
        if self.client:
            self.client.start()

    def load_user_data(self):
        self.load_avatar()
        self.load_users()
        self.load_contacts()

    def load_avatar(self):
        avatar = self.client.avatar
        self.avatar_changed.emit(avatar)

    def load_users(self):
        self.client.get_users_req()
        users = self.client.get_collection_response()
        users.remove(self.client.username)
        self.users_loaded.emit(users)

    def load_contacts(self):
        self.client.get_contacts_req()
        contacts = self.client.get_collection_response()
        self.contacts_loaded.emit(contacts)

    @try_except_wrapper
    def get_user_avatar(self, user):
        if user not in self.avatars.keys():
            avatar = self.client.get_user_avatar(user)
            self.avatars[user] = avatar
        else:
            avatar = self.avatars[user]
        return avatar

    def start_chat(self, username):
        self.curr_chat_user = username
        self.client.start_chat(username)

    def accepted_chat(self, resp):
        self.client.accepted_chat(resp)
        self.load_chat()

    @try_except_wrapper
    def load_chat(self, *args):
        self.client.get_chat_req(self.curr_chat_user)
        self.client.get_chat_sended = True
        chat = self.client.get_collection_response()
        self.client.get_chat_sended = False
        if chat:
            self.messages_loaded.emit(chat)

    @try_except_wrapper
    def decrypt_message(self, message):
        if self.curr_chat_user != '@ALL':
            message = self.client.get_encryptor(self.curr_chat_user)\
                             .decrypt_msg(message).decode()
        else:
            message = b64decode(message).decode()
        return message