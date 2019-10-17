import logging
import threading
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

import logs.server_log_config as log_config
from decorators import transaction

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


class ServerStorage:
    DB = 'sqlite:///server_db.db'
    sessions = {}

    def __init__(self):
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        self.database_engine = create_engine(self.DB, echo=False, pool_recycle=7200)
        Base.metadata.create_all(self.database_engine)
        self.session_factory = sessionmaker(bind=self.database_engine)

        # self.session = sessionmaker(bind=self.database_engine)()
        # self.session = self.get_session()

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


def main():
    import random

    storage = ServerStorage()
    ip = '127.0.0.1'
    user1 = f'User{random.randint(0, 100)}'
    user2 = f'User{random.randint(0, 100)}'

    storage.login_user(user1, ip)
    storage.login_user(user2, ip)
    print(f'Users online: {storage.get_users_online()}')

    storage.add_contact(user1, user2)
    print(f'{user1} contacts: {storage.get_contacts(user1)}')

    storage.remove_contact(user1, user2)
    print(f'{user1} contacts: {storage.get_contacts(user1)}')

    storage.logout_user(user1)
    print(f'Users online: {storage.get_users_online()}')


if __name__ == '__main__':
    main()
