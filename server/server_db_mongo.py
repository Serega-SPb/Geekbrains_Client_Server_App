import logging
from datetime import datetime
from hashlib import md5

from mongoengine import *
from mongoengine.queryset.visitor import Q

from logs import server_log_config as log_config
from metaclasses import Singleton


class History(EmbeddedDocument):
    datetime = DateTimeField()
    ip = StringField()


class User(Document):
    meta = {"collection": "users"}

    name = StringField(required=True)
    password = BinaryField(required=True)
    is_online = BooleanField(default=False)
    avatar = BinaryField()
    avatar_hash = StringField()
    contacts = ListField(ReferenceField('self'))
    history = ListField(EmbeddedDocumentField(History))


class Room(Document):
    meta = {"collection": "rooms"}

    name = StringField(required=True)


class Message(Document):
    meta = {"collection": "messages"}

    sender = ReferenceField(User, required=True)
    recipient = ReferenceField(User)
    text = StringField()
    time = DateTimeField()
    room = ReferenceField(Room)

    def get_chat_str(self):
        return f'{self.sender.name}__{str(self.time)}__{self.text}__{self.recipient.name}'

    def get_room_messages_str(self):
        return f'{self.sender.name}__{str(self.time)}__{self.text}__{self.room.name}'


class ServerStorageMongo(metaclass=Singleton):
    DB = 'mongodb://localhost:27017/local'

    def __init__(self, host=None):
        self.cursor = connect(host=host if host else self.DB)
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        User.objects(is_online=True).update(set__is_online=False)

    # region Transaction

    def register_user(self, username, password):
        user = User(name=username, password=password)
        user.save()
        return user

    def login_user(self, username, ip):
        user = User.objects(name=username).only('is_online', 'history').first()
        if not user:
            self.logger.error('DB.login_user: Unregistered user')
            return False

        hist = History(datetime=datetime.now(), ip=ip)
        user.update(set__is_online=True,
                    push__history=hist)

    def logout_user(self, username):
        user = User.objects(name=username).only('is_online').first()
        if user:
            user.update(set__is_online=False)

    def add_contact(self, username, contactname):
        user = User.objects(name=username).only('contacts').first()
        contact = User.objects(name=contactname).only('id').first()

        if not user or not contact:
            self.logger.error('DB.add_contact: user or contact not found')
            return False
        user.update(push__contacts=contact)

    def remove_contact(self, username, contactname):
        user = User.objects(name=username).only('contacts').first()
        contact = User.objects(name=contactname).only('id').first()

        if not user or not contact:
            self.logger.error('DB.remove_contact: user or contact not found')
            return False
        user.update(pull__contacts=contact)

    def add_message(self, sender_name, recipient_name, text):
        sender = User.objects(name=sender_name).only('id').first()
        recp = User.objects(name=recipient_name).only('id').first()

        if not sender or not recp:
            self.logger.error('DB.add_message: user not found')
            return False

        msg = Message(sender=sender, recipient=recp, text=text, time=datetime.now())
        msg.save()

    def set_avatar(self, username, avatar_bytes):
        user = User.objects(name=username).only('avatar', 'avatar_hash').first()
        if not user:
            self.logger.error('DB.set_avatar: user not found')
            return False
        user.update(set__avatar=avatar_bytes,
                    set__avatar_hash=md5(avatar_bytes).hexdigest())

    def create_room(self, room_name):
        room = Room.objects(name=room_name).first()
        if room:
            self.logger.error('DB.create_room: room already exists')
            return False
        room = Room(name=room_name)
        room.save()
        return room

    def add_message_to_room(self, room_name, message, username):
        user = User.objects(name=username).only('id').first()
        if not user:
            self.logger.error('DB.add_message_to_room: user not found')
            return False
        room = Room.objects(name=room_name).only('id').first()
        if not room:
            room = self.create_room(room_name)

        msg = Message(sender=user, room=room, text=message, time=datetime.now())
        msg.save()

    # endregion
    # region With return

    def authorization_user(self, username, password):
        user = User.objects(name=username).only('password').first()
        if not user:
            self.register_user(username, password)
            return True
        return user.password == password

    def get_users_online(self, *args):
        users = User.objects(is_online=True).only('name').all()
        return [u.name for u in users]

    def get_contacts(self, username):
        user = User.objects(name=username).only('contacts').first()
        if user:
            return [c.name for c in user.contacts]

    def get_chat(self, username_1, username_2):
        user_1 = User.objects(name=username_1).only('id').first()
        user_2 = User.objects(name=username_2).only('id').first()

        if not user_1 or not user_2:
            self.logger.error('DB.get_chat: user not found')
            return False

        return Message.objects\
            .filter((Q(sender=user_1) & Q(recipient=user_2)) | (Q(sender=user_2) & Q(recipient=user_1)))

    def get_chat_str(self, username_1, username_2):
        # TODO TEMP
        if username_1.startswith('@'):
            return self.get_room_messages_str(username_1[1:])
        if username_2.startswith('@'):
            return self.get_room_messages_str(username_2[1:])

        msgs = self.get_chat(username_1, username_2)
        return [m.get_chat_str() for m in msgs]

    def get_avatar(self, username):
        user = User.objects(name=username).only('avatar').first()
        if not user:
            self.logger.error('DB.get_avatar: user not found')
            return False
        return user.avatar if user.avatar else None

    def get_avatar_hash(self, username):
        user = User.objects(name=username).only('avatar_hash').first()
        if not user:
            self.logger.error('DB.get_avatar_hash: user not found')
            return False
        return user.avatar_hash if user.avatar_hash else None

    def check_avatar_hash(self, *args):
        username = args[-2]
        av_hash = args[-1]

        user = User.objects(name=username).only('avatar_hash').first()
        if not user:
            self.logger.error('DB.check_avatar_hash: user not found')
            return False
        if user.avatar_hash:
            return 1 if user.avatar_hash == av_hash else 0
        return 0

    def get_room_messages(self, room_name):
        room = Room.objects(name=room_name).only('id').first()
        if not room:
            self.logger.error('DB.get_room_messages: room not found')
            return False
        return Message.objects.filter(room=room)

    def get_room_messages_str(self, room_name):
        msgs = self.get_room_messages(room_name)
        return [m.get_room_messages_str() for m in msgs]

    # endregion
    # region Server UI

    def get_users(self):
        return User.objects.only('id', 'name', 'password').all()
        pass  # id name password

    def get_history(self):
        users = User.objects.only('id', 'name', 'history').all()
        result = []
        for u in users:
            for h in u.history:
                result.append((u, h))
        return result
        pass  # id name date ip

    def get_user_messages(self):
        return Message.objects(room=None).exclude('room').all()
        pass  # id sender recipient text time

    def get_users_avatar(self):
        return User.objects(avatar__ne=None).only('name', 'avatar_hash', 'avatar').all()
        pass  # name avatar_hash avatar

    # endregion
    # region Obsolete

    def user_stat_update(self, username, ch_sent=0, ch_recv=0):
        pass

    def get_user_stats(self):
        return None

    # endregion
