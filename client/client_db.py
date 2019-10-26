import logging
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import logs.client_log_config as log_config
from common.decorators import transaction
from common.metaclasses import Singleton

Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    contact = Column(String)

    def __init__(self, contact):
        self.contact = contact

    def __repr__(self):
        return f'<Contact({self.contact})>'


class ChatKey(Base):
    __tablename__ = 'chat_keys'
    id = Column(Integer, primary_key=True)
    user = Column(String)
    key = Column(String)

    def __init__(self, user, key):
        self.user = user
        self.key = key


class Message(Base):
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


class ClientStorage(metaclass=Singleton):
    DB = 'sqlite:///client_db.db'

    def __init__(self, username=None):
        db = f'sqlite:///{username}_db.db' if username else self.DB
        self.logger = logging.getLogger(log_config.LOGGER_NAME)
        self.database_engine = create_engine(db, echo=False, pool_recycle=7200)
        Base.metadata.create_all(self.database_engine)
        session_factory = sessionmaker(bind=self.database_engine)
        self.session = session_factory()

    @transaction
    def add_contact(self, contact):
        contact = Contact(contact)
        self.session.add(contact)

    @transaction
    def remove_contact(self, contact):
        self.session.query(Contact).filter_by(contact=contact).delete()

    def get_contact(self, contact):
        return self.session.query(Contact).filter_by(contact=contact).first()

    def get_contacts(self):
        return self.session.query(Contact).all()

    @transaction
    def add_message(self, recipient, text):
        message = Message(text, recipient, datetime.now())
        self.session.add(message)

    def get_messages(self):
        return self.session.query(Message).all()

    def append_contact(self, contact):
        check = self.session.query(Contact).filter_by(contact=contact).first()
        if check:
            return
        self.add_contact(contact)

    @transaction
    def add_chat_key(self, user, key):
        chat_key = ChatKey(user, key)
        self.session.add(chat_key)

    def get_key(self, user):
        key = self.session.query(ChatKey).filter_by(user=user).first()
        return key.key if key else None


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
