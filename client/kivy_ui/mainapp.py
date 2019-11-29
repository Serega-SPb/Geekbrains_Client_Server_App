import io
import logging
import re
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image, CoreImage

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


class LoginScreen(Screen):

    address = StringProperty()
    port = NumericProperty()
    username = StringProperty()
    password = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.address = '127.0.0.1'
        self.port = 7878
        self.username = 'Serega'
        self.password = 'qwer'


class UserBox(BoxLayout):
    def __init__(self, username, avatar, **kwargs):
        super().__init__(**kwargs)
        self.user = username
        self.ids['user_lbl'].value = username
        self.ids['user_avatar'].texture = avatar

    def start_chat_link(self, func):
        self.ids['start_chat_btn'].on_touch_down = lambda t: func(self.user) if self.collide_point(*t.pos) else None


class ProfileScreen(Screen):
    avatar = Image()
    username = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = ClientAppStorage()
        self.logger = self.storage.logger
        self.storage.username_changed += self.set_username
        self.storage.avatar_changed += self.set_avatar
        self.storage.users_loaded += self.set_users
        self.storage.contacts_loaded += self.set_contacts
        self.storage.user_connected += lambda u: self.add_user_in_list(self.users_list, u)
        self.storage.user_disconnected += lambda u: self.remove_user_from_list(self.users_list, u)
        # self.storage.accepted_chat_ev += lambda x: self.open_messanger()

    @property
    def users_list(self):
        return self.ids['users_list']

    @property
    def contacts_list(self):
        return self.ids['contacts_list']

    def open_filter(self, sender, touch):
        if sender.collide_point(*touch.pos) and touch.is_double_tap:
            self.manager.current = 'image_filter'

    def open_messanger(self):
        self.manager.current = 'messanger'

    def set_username(self, username):
        self.username = username

    def set_avatar(self, avatar_bytes):
        if not avatar_bytes:
            return
        img = io.BytesIO(avatar_bytes)
        texture = CoreImage(img, ext='png').texture
        self.avatar.texture = texture

    @try_except_wrapper
    def add_user_in_list(self, ui_list, user):
        avatar_bytes = self.storage.get_user_avatar(user)
        avatar_texture = None
        if avatar_bytes:
            avatar_texture = CoreImage(io.BytesIO(avatar_bytes), ext='png').texture
        wid = UserBox(user, avatar_texture)
        wid.start_chat_link(self.init_chat)
        ui_list_len = len(ui_list.children)
        ui_list.add_widget(wid, ui_list_len - 1)
        ui_list.height = ui_list_len * 50

    @try_except_wrapper
    def remove_user_from_list(self, ui_list, user):
        for wid in ui_list.children:
            if hasattr(wid, 'user') and wid.user == user:
                ui_list.remove_widget(wid)
                ui_list.height = (len(ui_list.children) - 1) * 50
                break

    @try_except_wrapper
    def set_users(self, users):
        users_list = self.users_list
        for u in users:
            self.add_user_in_list(users_list, u)

    @try_except_wrapper
    def set_contacts(self, contacts):
        contacts_list = self.contacts_list
        for c in contacts:
            self.add_user_in_list(contacts_list, c)

    def init_chat(self, user):
        self.storage.start_chat(user)
        self.manager.current = 'messanger'


class MessageBox(BoxLayout):

    user = StringProperty()
    time = StringProperty()
    msg = StringProperty()

    FORMAT_PATTERN = {
        r'\*\*(.+)\*\*': r'[b]\1[/b]',
        '__(.+)__': r'[u]\1[/u]',
        '##(.+)##': r'[i]\1[/i]',
    }

    def __init__(self,user, time, msg,  **kwargs):
        super().__init__(**kwargs)
        self.user = user
        self.time = time
        self.msg = self.apply_format(msg)

    def apply_format(self, text):
        text = text.strip()
        for pat, fmt in self.FORMAT_PATTERN.items():
            text = re.sub(pat, fmt, text)
        return text


class MessangerScreen(Screen):
    TIME_FMT = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = ClientAppStorage()
        self.logger = self.storage.logger

        self.storage.messages_loaded += lambda msgs: [self.parse_message(m) for m in msgs] if msgs else None
        self.storage.got_message += self.recieve_message

    @property
    def chat_list(self):
        return self.ids['chat_list']

    @property
    def mesasge_input(self):
        return self.ids['mesasge_input']

    def add_message_in_chat(self, user, msg, time):
        if self.storage.curr_chat_user != '@ALL' and \
                user not in [self.storage.curr_chat_user, self.storage.client.username]:
            return
        msg_wid = MessageBox(user, time, msg)
        ui_list = self.chat_list
        ui_list_len = len(ui_list.children)
        ui_list.add_widget(msg_wid, ui_list_len - 1)
        ui_list.height = sum([w.height for w in ui_list.children[:-1]])

    def recieve_message(self, msg):
        sender, msg = self.client.parse_recv_message(msg)
        time = datetime.now().strftime('%H:%M')
        self.add_message_in_chat(sender, msg, time)

    def parse_message(self, msg):
        sender, time, message, *_ = msg.split('__')
        time = datetime.strptime(time, self.TIME_FMT).strftime('%H:%M')
        message = self.storage.decrypt_message(message)
        self.add_message_in_chat(sender, message, time)

    def send_message(self):
        user = self.storage.curr_chat_user
        msg = self.mesasge_input.text
        time = datetime.now().strftime('%H:%M')
        self.storage.client.send_msg(msg, user)
        self.add_message_in_chat(user, msg, time)


class MainApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = ClientAppStorage()
        self.logger = self.storage.logger

    @try_except_wrapper
    def login(self, *args):
        self.storage.init_client(*args)
        self.storage.start_client()
        self.storage.load_user_data()


if __name__ == '__main__':
    MainApp().run()
