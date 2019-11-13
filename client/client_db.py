""" Module implements client database models """

import logging
from base64 import b64encode, b64decode
from hashlib import md5
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Binary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from logs import client_log_config as log_config
from decorators import transaction
from metaclasses import Singleton

Base = declarative_base()


class Contact(Base):
    """ Class model of Contacts table """

    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    contact = Column(String)

    def __init__(self, contact):
        self.contact = contact

    def __repr__(self):
        return f'<Contact({self.contact})>'


class ChatKey(Base):
    """ Class model of Chat keys table """

    __tablename__ = 'chat_keys'
    id = Column(Integer, primary_key=True)
    user = Column(String)
    key = Column(String)

    def __init__(self, user, key):
        self.user = user
        self.key = key


class Message(Base):
    """ Class model of Messages table """

    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    recipient = Column(String)
    time = Column(DateTime)

    def __init__(self, text, recipient, time):
        self.text = text
        self.recipient = recipient
        self.time = time

    def __repr__(self):
        return f'<Message({self.recipient}, {self.text})>'


class Avatar(Base):
    __tablename__ = 'avatars'
    id = Column(Integer, primary_key=True)
    user = Column(String)
    avatar = Column(Binary)
    avatar_hash = Column(String)

    def __init__(self, user, avatar_bytes):
        self.user = user
        self.set_avatar(avatar_bytes)

    def set_avatar(self, avatar_bytes):
        self.avatar = avatar_bytes
        self.avatar_hash = md5(avatar_bytes).hexdigest()
        # self.avatar_hash = hash(avatar_bytes)


class ClientStorage(metaclass=Singleton):
    """ Class a connector to database """

    DB = 'sqlite:///user_data/client_db.db'

    def __init__(self, username=None):
        db = self.DB.replace('client', username) if username else self.DB
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        self.database_engine = create_engine(db, echo=False, pool_recycle=7200)
        Base.metadata.create_all(self.database_engine)
        session_factory = sessionmaker(bind=self.database_engine)
        self.session = session_factory()

    @transaction
    def add_contact(self, contact):
        """ Method adds contact in db """

        contact = Contact(contact)
        self.session.add(contact)

    @transaction
    def remove_contact(self, contact):
        """ Method removes contact in db """

        self.session.query(Contact).filter_by(contact=contact).delete()

    def get_contact(self, contact):
        """ Method gets contact from db """

        return self.session.query(Contact).filter_by(contact=contact).first()

    def get_contacts(self):
        """ Method gets contacts from db """

        return self.session.query(Contact).all()

    @transaction
    def add_message(self, recipient, text):
        """ Method adds message in db """

        message = Message(text, recipient, datetime.now())
        self.session.add(message)

    def get_messages(self):
        """ Method gets messages from db """

        return self.session.query(Message).all()

    def append_contact(self, contact):
        """ Method appends contact if not exist """

        check = self.session.query(Contact).filter_by(contact=contact).first()
        if check:
            return
        self.add_contact(contact)

    @transaction
    def add_chat_key(self, user, key):
        """ Method adds key to contact in db """

        chat_key = ChatKey(user, key)
        self.session.add(chat_key)

    def get_key(self, user):
        """ Method gets key of contact from db """

        key = self.session.query(ChatKey).filter_by(user=user).first()
        return key.key if key else None

    @transaction
    def set_avatar(self, user, avatar_bytes):
        avatar = self.session.query(Avatar).filter_by(user=user).first()
        if not avatar:
            avatar = Avatar(user, avatar_bytes)
            self.session.add(avatar)
        else:
            avatar.set_avatar(avatar_bytes)

    def get_avatar(self, user):
        avatar = self.session.query(Avatar).filter_by(user=user).first()
        return avatar if avatar else None

    def get_avatar_hash(self, user):
        avatar = self.session.query(Avatar).filter_by(user=user).first()
        return avatar.avatar_hash if avatar else None


def main():
    import random

    storage = ClientStorage()
    contact = f'Contact{random.randint(0, 100)}'

    storage.add_contact(contact)
    print(f'Contacts: {storage.get_contacts()}')

    storage.remove_contact(contact)
    print(f'Contacts: {storage.get_contacts()}')

    storage.add_message(contact, 'Test msg')
    print(f'Messages: {storage.get_messages()}')


if __name__ == '__main__':
    main()
