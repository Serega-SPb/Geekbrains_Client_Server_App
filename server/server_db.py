""" Module implements server database models """

import logging
import threading
from datetime import datetime
from hashlib import md5

from sqlalchemy import create_engine, or_, and_, Column, ForeignKey, \
                       Integer, String, DateTime, Binary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, aliased

from logs import server_log_config as log_config
from decorators import transaction
from metaclasses import Singleton

Base = declarative_base()


class User(Base):
    """ Class model of Users table """

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    password = Column(String)

    def __init__(self, name, password):
        self.name = name
        self.password = password

    def __repr__(self):
        return f'<User({self.name})>'

    def __str__(self):
        return self.name


class UserOnline(Base):
    """ Class model of Users online table """

    __tablename__ = 'online'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    def __init__(self, user_id):
        self.user_id = user_id


class LoginHistory(Base):
    """ Class model of History table """

    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    datetime = Column(DateTime)
    ip = Column(String)

    def __init__(self, user_id, time, ip):
        self.user_id = user_id
        self.datetime = time
        self.ip = ip


class Contact(Base):
    """ Class model of Contacts table """

    __tablename__ = 'contacts'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    contact_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    def __init__(self, user_id, contact_id):
        self.user_id = user_id
        self.contact_id = contact_id


class UserStat(Base):
    """ Class model of User stats table """

    __tablename__ = 'user_stats'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    mes_sent = Column(Integer, default=0)
    mes_recv = Column(Integer, default=0)

    def __init__(self, user_id):
        self.user_id = user_id
        self.mes_recv = 0
        self.mes_sent = 0


class UserMessage(Base):
    """ Class model of User messages table """

    __tablename__ = 'user_messages'
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'))
    recipient_id = Column(Integer, ForeignKey('users.id'))
    text = Column(String)
    time = Column(DateTime)

    def __init__(self, sender_id, recipient_id, text, time):
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.text = text
        self.time = time

    def __str__(self):
        return f'{self.time}__{self.text}'


class UserAvatar(Base):
    __tablename__ = 'user_avatars'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    avatar = Column(Binary)
    avatar_hash = Column(String)

    def __init__(self, user_id, avatar_bytes):
        self.user_id = user_id
        self.set_avatar(avatar_bytes)

    def set_avatar(self, avatar_bytes):
        self.avatar = avatar_bytes
        self.avatar_hash = md5(avatar_bytes).hexdigest()
        # self.avatar_hash = hash(avatar_bytes)


class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name


class RoomMessage(Base):
    __tablename__ = 'room_messages'

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('rooms.id'))
    message = Column(String)
    sender_id = Column(Integer, ForeignKey('users.id'))
    time = Column(DateTime)

    def __init__(self, room_id, message, sender_id, time):
        self.room_id = room_id
        self.message = message
        self.sender_id = sender_id
        self.time = time

    def __str__(self):
        return f'{self.time}__{self.message}'


class ServerStorage(metaclass=Singleton):
    """ Class a connector to database """

    DB = 'sqlite:///server_db.db'
    sessions = {}

    def __init__(self, db_file=None):
        self.set_database(db_file)

    def set_database(self, db_file):
        """ Method the create connection to db """

        db = f'sqlite:///{db_file}' if db_file else self.DB
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        self.database_engine = create_engine(db, echo=False, pool_recycle=7200)
        Base.metadata.create_all(self.database_engine)
        self.session_factory = sessionmaker(bind=self.database_engine)

        self.session.query(UserOnline).delete()
        self.session.commit()

    @property
    def session(self):
        thread = threading.current_thread().name
        if thread in self.sessions:
            return self.sessions[thread]
        else:
            session = scoped_session(self.session_factory)()
            self.sessions[thread] = session
            return session

    @transaction
    def register_user(self, username, password):
        """ Method the registration new user """

        user = User(username, password)
        self.session.add(user)
        return user

    def get_users(self):
        """ Method gets users from db """

        return self.session.query(User).all()

    def authorization_user(self, username, password):
        """ Method authorization user """

        user = self.session.query(User).filter_by(name=username).first()
        if not user:
            self.register_user(username, password)
            return True
        return user.password == password

    @transaction
    def login_user(self, username, ip):
        """ Method the login user """

        user = self.session.query(User).filter_by(name=username).first()
        if not user:
            self.logger.error('DB.login_user: Unregistered user')
            return

        online = UserOnline(user.id)
        self.session.add(online)
        hist = LoginHistory(user.id, datetime.now(), ip)
        self.session.add(hist)

    @transaction
    def logout_user(self, username):
        """ Method the logout user """

        user = self.session.query(User).filter_by(name=username).first()
        if user:
            self.session.query(UserOnline).filter_by(user_id=user.id).delete()

    def get_history(self):
        return self.session.query(User, LoginHistory)\
            .join(LoginHistory, User.id == LoginHistory.user_id).all()

    @transaction
    def add_contact(self, username, contactname):
        """ Method adds contact to user in db """

        user = self.session.query(User).filter_by(name=username).first()
        contact = self.session.query(User).filter_by(name=contactname).first()

        if not user or not contact:
            self.logger.error('DB.add_contact: user or contact not found')
            return False

        relation = Contact(user.id, contact.id)
        self.session.add(relation)

    @transaction
    def remove_contact(self, username, contactname):
        """ Method removes contact from user in db """

        user = self.session.query(User).filter_by(name=username).first()
        contact = self.session.query(User).filter_by(name=contactname).first()

        if not user or not contact:
            self.logger.error('DB.remove_contact: user or contact not found')
            return False

        self.session.query(Contact)\
            .filter_by(user_id=user.id, contact_id=contact.id).delete()

    def get_users_online(self, *args):
        """ Method gets users online from db """

        return self.session.query(User).join(UserOnline).all()

    def get_contacts(self, username):
        """ Method gets user contacts from db """

        user = self.session.query(User).filter_by(name=username).first()
        if user:
            return self.session.query(User)\
                .join(Contact, User.id == Contact.contact_id)\
                .filter(Contact.user_id == user.id)\
                .all()

    @transaction
    def user_stat_update(self, username, ch_sent=0, ch_recv=0):
        """ Method updates user statistics """

        user = self.session.query(User).filter_by(name=username).first()
        if not user:
            self.logger.error('DB.user_stat_update: user not found')
            return False

        stat = self.session.query(UserStat).filter_by(user_id=user.id).first()
        if not stat:
            stat = UserStat(user.id)
            self.session.add(stat)

        stat.mes_sent += ch_sent
        stat.mes_recv += ch_recv

    def get_user_stats(self):
        """ Method gets user statistics """

        return self.session.query(User, UserStat)\
            .join(UserStat, User.id == UserStat.user_id).all()

    @transaction
    def add_message(self, sender_name, recipient_name, text):
        """ Method adds message in db """

        sender = self.session.query(User).filter_by(name=sender_name).first()
        recp = self.session.query(User).filter_by(name=recipient_name).first()

        if not sender or not recp:
            self.logger.error('DB.add_message: user not found')
            return False

        msg = UserMessage(sender.id, recp.id, text, datetime.now())
        self.session.add(msg)

    def get_user_messages(self):
        """ Method gets users messages from db """

        senders = aliased(User)
        recipients = aliased(User)

        return self.session.query(senders, UserMessage, recipients)\
            .join(senders, UserMessage.sender_id == senders.id) \
            .join(recipients, UserMessage.recipient_id == recipients.id) \
            .all()

    def get_chat(self, username_1, username_2):
        """ Method gets users chat messages from db """

        user_1 = self.session.query(User).filter_by(name=username_1).first()
        user_2 = self.session.query(User).filter_by(name=username_2).first()

        if not user_1 or not user_2:
            self.logger.error('DB.get_chat: user not found')
            return False

        senders = aliased(User)
        recipients = aliased(User)

        msgs = self.session.query(senders, UserMessage, recipients)\
            .join(senders, UserMessage.sender_id == senders.id) \
            .join(recipients, UserMessage.recipient_id == recipients.id) \
            .filter(or_(
                and_(UserMessage.sender_id == user_1.id,
                     UserMessage.recipient_id == user_2.id),
                and_(UserMessage.sender_id == user_2.id,
                     UserMessage.recipient_id == user_1.id)
            )).all()
        return msgs

    def get_chat_str(self, username_1, username_2):
        """ Method gets users chat messages from db as formatted strings"""

        # TODO TEMP
        if username_1.startswith('@'):
            return self.get_room_messages_str(username_1[1:])
        if username_2.startswith('@'):
            return self.get_room_messages_str(username_2[1:])

        msgs = self.get_chat(username_1, username_2)
        return list(['__'.join(tuple(str(m) for m in msg)) for msg in msgs])

    @transaction
    def set_avatar(self, username, avatar_bytes):
        user = self.session.query(User).filter_by(name=username).first()
        if not user:
            self.logger.error('DB.set_avatar: user not found')
            return False
        u_avatar = self.session.query(UserAvatar).filter_by(user_id=user.id).first()
        if not u_avatar:
            u_avatar = UserAvatar(user.id, avatar_bytes)
            self.session.add(u_avatar)
        else:
            u_avatar.set_avatar(avatar_bytes)

    def get_avatar_hash(self, username):
        user = self.session.query(User).filter_by(name=username).first()
        if not user:
            self.logger.error('DB.get_avatar_hash: user not found')
            return False
        a = self.session.query(UserAvatar).filter_by(user_id=user.id).first()
        return a.avatar_hash if a else None

    def get_avatar(self, username):
        user = self.session.query(User).filter_by(name=username).first()
        if not user:
            self.logger.error('DB.get_avatar: user not found')
            return False
        a = self.session.query(UserAvatar).filter_by(user_id=user.id).first()
        return a.avatar if a else None

    def check_avatar_hash(self, *args):
        username = args[-2]
        av_hash = args[-1]

        user = self.session.query(User).filter_by(name=username).first()
        if not user:
            self.logger.error('DB.check_avatar_hash: user not found')
            return False
        answer = self.session.query(UserAvatar).filter(and_(
                UserAvatar.user_id == user.id,
                UserAvatar.avatar_hash == av_hash
            )).first()
        return 1 if answer else 0

    def get_users_avatar(self):
        return self.session.query(User, UserAvatar)\
            .join(User, UserAvatar.user_id == User.id).all()

    @transaction
    def create_room(self, room_name):
        room = self.session.query(Room).filter_by(name=room_name).first()
        if room:
            self.logger.error('DB.create_room: room already exists')
            return False
        room = Room(room_name)
        self.session.add(room)
        return room

    def get_rooms(self):
        return self.session.query(Room).all()

    @transaction
    def add_message_to_room(self, room_name, message, username):
        user = self.session.query(User).filter_by(name=username).first()
        if not user:
            self.logger.error('DB.add_message_to_room: user not found')
            return False
        room = self.session.query(Room).filter_by(name=room_name).first()
        if not room:
            room = self.create_room(room_name)
        room_msg = RoomMessage(room.id, message, user.id, datetime.now())
        self.session.add(room_msg)

    def get_room_messages(self, room_name):
        room = self.session.query(Room).filter_by(name=room_name).first()
        if not room:
            self.logger.error('DB.get_room_messages: room not found')
            return False

        msgs = self.session.query(User, RoomMessage)\
            .join(User, RoomMessage.sender_id == User.id)\
            .filter(RoomMessage.room_id == room.id)\
            .all()
        return msgs

    def get_room_messages_str(self, room_name):
        msgs = self.get_room_messages(room_name)
        return list(['__'.join(tuple(str(m) for m in msg)) for msg in msgs])


def main():
    import random

    storage = ServerStorage()
    ip = '127.0.0.1'
    user1 = f'User{random.randint(0, 100)}'
    user2 = f'User{random.randint(0, 100)}'
    room = 'ALL'

    # storage.create_room(room)
    # storage.add_message_to_room(room, 'test_msg', 'Serega')
    # rch = storage.get_room_messages(room)
    rch_s = storage.get_room_messages_str(room)

    # st = storage.get_user_stats()
    # hist = storage.get_history()
    avs = storage.get_users_avatar()

    storage.login_user(user1, ip)
    storage.login_user(user2, ip)

    storage.add_message(user1, user2, 'U1 send to U2')
    storage.add_message(user2, user1, 'U2 send to U1')

    msgs = storage.get_user_messages()
    print(msgs)
    chat = storage.get_chat_str(user1, user2)
    print(chat)

    print(f'Users online: {storage.get_users_online()}')

    storage.add_contact(user1, user2)
    print(f'{user1} contacts: {storage.get_contacts(user1)}')

    storage.remove_contact(user1, user2)
    print(f'{user1} contacts: {storage.get_contacts(user1)}')

    storage.logout_user(user1)
    print(f'Users online: {storage.get_users_online()}')


if __name__ == '__main__':
    main()
