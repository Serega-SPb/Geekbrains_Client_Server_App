import io
import re
import os
from datetime import datetime

from kivy.app import App
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image, CoreImage
from PIL import Image as PImage


from decorators import try_except_wrapper
from kivy_ui.client_storage import ClientAppStorage


class LoginScreen(Screen):

    address = StringProperty()
    port = NumericProperty()
    username = StringProperty()
    password = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = ClientAppStorage()
        self.logger = self.storage.logger
        self.address = '127.0.0.1'
        self.port = 7878
        self.username = 'Serega'
        self.password = 'qwer'

    @try_except_wrapper
    def login(self, *args):
        self.storage.init_client(*args)
        self.storage.start_client()
        self.storage.load_user_data()
        self.manager.current = 'main'


class UserBox(BoxLayout):
    def __init__(self, username, avatar, **kwargs):
        super().__init__(**kwargs)
        self.user = username
        self.ids['user_lbl'].value = username
        self.ids['user_avatar'].texture = avatar

    def start_chat_link(self, func):
        chat_btn = self.ids['start_chat_btn']
        chat_btn.bind(on_press=lambda x: func(self.user))

    def set_action(self, name, action):
        action_btn = self.ids['action_btn']
        action_btn.text = name
        action_btn.bind(on_press=lambda x: action(self.user))


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

    @property
    def users_list(self):
        return self.ids['users_list']

    @property
    def contacts_list(self):
        return self.ids['contacts_list']

    def open_filter(self, sender, touch):
        if sender.collide_point(*touch.pos) and touch.is_double_tap:
            self.manager.current = 'image_filter'

    def open_chat_room_all(self):
        self.storage.curr_chat_user = '@ALL'
        self.storage.load_chat()

    def set_username(self, username):
        self.username = username

    def set_avatar(self, avatar_bytes):
        if not avatar_bytes:
            return
        img = io.BytesIO(avatar_bytes)
        texture = CoreImage(img, ext='png').texture
        self.avatar.texture = texture

    @try_except_wrapper
    def add_contact(self, username):
        self.storage.client.add_contact(username)
        self.storage.client.answers.get()
        self.add_user_in_list(self.contacts_list, username,
                              'DEL', self.remove_contact)

    @try_except_wrapper
    def remove_contact(self, username):
        self.storage.client.rem_contact(username)
        self.storage.client.answers.get()
        self.remove_user_from_list(self.contacts_list, username)

    @try_except_wrapper
    def add_user_in_list(self, ui_list, user, action_name, action):
        avatar_bytes = self.storage.get_user_avatar(user)
        avatar_texture = None
        if avatar_bytes:
            avatar_texture = CoreImage(io.BytesIO(avatar_bytes), ext='png').texture
        wid = UserBox(user, avatar_texture)
        wid.start_chat_link(self.storage.start_chat)
        wid.set_action(action_name, action)
        ui_list.add_widget(wid)
        self.update_list_height(ui_list)

    @try_except_wrapper
    def remove_user_from_list(self, ui_list, user):
        for wid in ui_list.children:
            if hasattr(wid, 'user') and wid.user == user:
                ui_list.remove_widget(wid)
                self.update_list_height(ui_list)
                break

    def update_list_height(self, ui_list):
        ui_list_len = len(ui_list.children)
        ui_list.height = ui_list_len * 50

    @try_except_wrapper
    def set_users(self, users):
        users_list = self.users_list
        for u in users:
            self.add_user_in_list(users_list, u, 'ADD', self.add_contact)

    @try_except_wrapper
    def set_contacts(self, contacts):
        contacts_list = self.contacts_list
        for c in contacts:
            self.add_user_in_list(contacts_list, c, 'DEL', self.remove_contact)


class MessageBox(BoxLayout):

    user = StringProperty()
    time = StringProperty()
    msg = StringProperty()

    text_height = NumericProperty()

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
        self.text_height = (text.count('\n') + 1) * 50
        for pat, fmt in self.FORMAT_PATTERN.items():
            text = re.sub(pat, fmt, text)
        return text


class MessengerScreen(Screen):
    TIME_FMT = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = ClientAppStorage()
        self.logger = self.storage.logger

        self.storage.messages_loaded += self.load_chat
        self.storage.got_message += self.recieve_message

    @property
    def header(self):
        return self.ids['header']

    @property
    def chat_list(self):
        return self.ids['chat_list']

    @property
    def mesasge_input(self):
        return self.ids['mesasge_input']

    def load_chat(self, msgs):
        # [self.chat_list.remove_widget(wid) for wid in self.chat_list.children]
        self.chat_list.clear_widgets()
        if msgs:
            [self.parse_message(m) for m in msgs]
        self.header.value = f'Chat with {self.storage.curr_chat_user}'
        self.manager.current = 'messenger'

    def add_message_in_chat(self, user, msg, time):
        if self.storage.curr_chat_user != '@ALL' and \
                user not in [self.storage.curr_chat_user, self.storage.client.username]:
            return
        msg_wid = MessageBox(user, time, msg)
        ui_list = self.chat_list
        ui_list_len = len(ui_list.children)
        ui_list.add_widget(msg_wid)
        # print([w.height for w in ui_list.children])
        ui_list.height = sum([w.height for w in ui_list.children])
        # print(ui_list.height)

    def recieve_message(self, msg):
        sender, msg, recipient = self.client.parse_recv_message(msg)
        if (recipient == '@ALL' and self.curr_chat_user == '@ALL') or \
                (recipient != '@ALL' and sender == self.curr_chat_user):
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
        self.add_message_in_chat(self.storage.client.username, msg, time)
        self.mesasge_input.text = ''


class ImageFilterScreen(Screen):
    start_point_x = NumericProperty(0)
    start_point_y = NumericProperty(0)

    end_point_x = NumericProperty(0)
    end_point_y = NumericProperty(0)

    p_image = None
    image_size = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = ClientAppStorage()
        self.logger = self.storage.logger
        self.storage.image_selected += self.set_image

    @property
    def image(self):
        return self.ids['image']

    @property
    def wrapper(self):
        return self.ids['wrapper']

    def box_on_touch_down(self, sender, touch):
        if not sender.collide_point(*touch.pos):
            return
        self.start_point_x = touch.x
        self.start_point_y = touch.y
        self.end_point_x = 0
        self.end_point_y = 0
        touch.grab(sender)

    def box_on_touch_move(self, sender, touch):
        if not sender.collide_point(*touch.pos):
            return
        if touch.grab_current is sender:
            self.end_point_x = touch.x - self.start_point_x
            self.end_point_y = touch.y - self.start_point_y

    def box_on_touch_up(self, sender, touch):
        if not sender.collide_point(*touch.pos):
            return
        if touch.grab_current is sender:
            self.end_point_x = touch.x - self.start_point_x
            self.end_point_y = touch.y - self.start_point_y

            self.select_area()

    def select_area(self):
        self.update_image()
        self.start_point_x = 0
        self.start_point_y = 0
        self.end_point_x = 0
        self.end_point_y = 0

    def set_image(self, img_file):
        self.image.source = ''
        self.p_image = PImage.open(img_file)
        self.image_size = self.p_image.size
        self.wrapper.size_hint = (1, 0) if self.image_size[0] > self.image_size[1] else (0, 1)
        self.image.source = img_file

    @try_except_wrapper
    def update_image(self):
        d = self.image.norm_image_size[0] / self.image.texture.size[0]
        st_x, st_y = self.start_point_x, self.start_point_y
        en_x, en_y = self.end_point_x, self.end_point_y
        w, h = self.p_image.size

        x1, y1 = st_x/d, h - st_y/d
        x2, y2 = st_x/d + en_x/d, h - st_y/d + en_y/d

        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        self.p_image = self.p_image.crop((x1, y1, x2, y2))
        buf = io.BytesIO()
        self.p_image.save(buf, 'PNG')
        buf.seek(0)
        c_img = CoreImage(buf, ext='png')
        self.image.texture = c_img.texture
        print(self.image.size)
        self.wrapper.size_hint = (1, 0) if self.image_size[0] > self.image_size[1] else (0, 1)

    def make_square(self, im, min_size=256, fill_color=(0, 0, 0, 0)):
        x, y = im.size
        size = max(min_size, x, y)
        new_im = PImage.new('RGBA', (size, size), fill_color)
        new_im.paste(im, (int((size - x) / 2), int((size - y) / 2)))
        return new_im

    def apply_avatar(self):
        img = self.image.texture
        buf = io.BytesIO()
        img.save(buf, False, fmt='png')
        p_img = PImage.open(buf)
        # p_img = self.p_image
        p_img = self.make_square(p_img)
        p_img.thumbnail((48, 48), PImage.ANTIALIAS)
        buf = io.BytesIO()
        p_img.save(buf, 'PNG')
        img_bytes = buf.getvalue()
        self.storage.client.avatar = img_bytes
        self.storage.load_avatar()
        self.manager.current = 'profile'

    def cancel(self):
        self.image.source = ''
        self.manager.current = 'profile'


class OpenFileScreen(Screen):

    file = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = ClientAppStorage()

    @property
    def chooser(self):
        return self.ids['file_chooser']

    def open(self):
        chooser = self.chooser
        path = chooser.path
        selected_files = chooser.selection
        self.file = os.path.join(path, selected_files[0])
        if os.path.isfile(self.file):
            self.storage.image_selected.emit(self.file)
        self.manager.current = 'image_filter'

    def cancel(self):
        self.file = ''
        self.manager.current = 'image_filter'


class MainApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


if __name__ == '__main__':
    MainApp().run()
