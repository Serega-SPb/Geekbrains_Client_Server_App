import logging
import threading
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, or_, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, aliased

import logs.server_log_config as log_config
from common.decorators import transaction
from common.metaclasses import Singleton

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<User({self.name})>'

    def __str__(self):
        return self.name


class UserOnline(Base):
    __tablename__ = 'online'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    def __init__(self, user_id):
        self.user_id = user_id


class LoginHistory(Base):
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
    __tablename__ = 'contacts'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    contact_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    def __init__(self, user_id, contact_id):
        self.user_id = user_id
        self.contact_id = contact_id


class UserStat(Base):
    __tablename__ = 'user_stats'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    mes_sent = Column(Integer, default=0)
    mes_recv = Column(Integer, default=0)

    def __init__(self, user_id):
        self.user_id = user_id
        self.mes_recv = 0
        self.mes_sent = 0


class UserMessage(Base):
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


class ServerStorage(metaclass=Singleton):
    DB = 'sqlite:///server_db.db'
    sessions = {}

    def __init__(self, db_file=None):
        self.set_database(db_file)

    def set_database(self, db_file):
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
    def register_user(self, username):
        user = User(username)
        self.session.add(user)
        return user

    def get_users(self):
        return self.session.query(User).all()

    @transaction
    def login_user(self, username, ip):
        print(threading.current_thread())
        user = self.session.query(User).filter_by(name=username).first()
        if not user:
            user = self.register_user(username)

        online = UserOnline(user.id)
        self.session.add(online)
        hist = LoginHistory(user.id, datetime.now(), ip)
        self.session.add(hist)

    @transaction
    def logout_user(self, username):
        user = self.session.query(User).filter_by(name=username).first()
        if user:
            self.session.query(UserOnline).filter_by(user_id=user.id).delete()

    def get_history(self):
        return self.session.query(User, LoginHistory).join(LoginHistory, User.id == LoginHistory.user_id).all()

    @transaction
    def add_contact(self, username, contactname):
        user = self.session.query(User).filter_by(name=username).first()
        contact = self.session.query(User).filter_by(name=contactname).first()

        if not user or not contact:
            self.logger.error('DB.add_contact: user or contact not found')
            return False

        relation = Contact(user.id, contact.id)
        self.session.add(relation)

    @transaction
    def remove_contact(self, username, contactname):
        user = self.session.query(User).filter_by(name=username).first()
        contact = self.session.query(User).filter_by(name=contactname).first()

        if not user or not contact:
            self.logger.error('DB.remove_contact: user or contact not found')
            return False

        self.session.query(Contact).filter_by(user_id=user.id, contact_id=contact.id).delete()

    def get_users_online(self, *args):
        return self.session.query(User).join(UserOnline).all()

    def get_contacts(self, username):
        user = self.session.query(User).filter_by(name=username).first()
        if user:
            return self.session.query(User)\
                .join(Contact, User.id == Contact.contact_id)\
                .filter(Contact.user_id == user.id)\
                .all()

    @transaction
    def user_stat_update(self, username, ch_sent=0, ch_recv=0):
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
        return self.session.query(User, UserStat).join(UserStat, User.id == UserStat.user_id).all()

    @transaction
    def add_message(self, sender_name, recipient_name, text):

        sender = self.session.query(User).filter_by(name=sender_name).first()
        recipient = self.session.query(User).filter_by(name=recipient_name).first()

        if not sender or not recipient:
            self.logger.error('DB.add_message: user not found')
            return False

        msg = UserMessage(sender.id, recipient.id, text, datetime.now())
        self.session.add(msg)

    def get_user_messages(self):
        senders = aliased(User)
        recipients = aliased(User)

        return self.session.query(senders, UserMessage, recipients)\
            .join(senders, UserMessage.sender_id == senders.id) \
            .join(recipients, UserMessage.recipient_id == recipients.id) \
            .all()

    def get_chat(self, username_1, username_2):

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
                and_(UserMessage.sender_id == user_1.id, UserMessage.recipient_id == user_2.id),
                and_(UserMessage.sender_id == user_2.id, UserMessage.recipient_id == user_1.id)
            )).all()
        return msgs

    def get_chat_str(self, username_1, username_2):
        msgs = self.get_chat(username_1, username_2)
        return list(['__'.join(tuple(str(m) for m in msg)) for msg in msgs])


def main():
    import random

    storage = ServerStorage()
    ip = '127.0.0.1'
    user1 = f'User{random.randint(0, 100)}'
    user2 = f'User{random.randint(0, 100)}'

    # st = storage.get_user_stats()
    # hist = storage.get_history()

    storage.login_user(user1, ip)
    storage.login_user(user2, ip)

    storage.add_message(user1, user2, 'U1 send to U2')
    storage.add_message(user2, user1, 'U2 send to U1')

    msgs = storage.get_user_messages()
    chat = storage.get_chat_str(user1, user2)

    print(f'Users online: {storage.get_users_online()}')

    storage.add_contact(user1, user2)
    print(f'{user1} contacts: {storage.get_contacts(user1)}')

    storage.remove_contact(user1, user2)
    print(f'{user1} contacts: {storage.get_contacts(user1)}')

    storage.logout_user(user1)
    print(f'Users online: {storage.get_users_online()}')


if __name__ == '__main__':
    main()
