import sys

from server_db import ServerStorage
from server_db_mongo import *


def load_users_to_mongo(users, history, avatars):
    for user in users:
        m_user = User.objects(name=user.name).first()
        if m_user:
            continue
        m_user = User()
        m_user.name = user.name
        m_user.password = user.password
        avatar = [av[1] for av in avatars if av[1].user_id == user.id]
        if avatar:
            avatar = avatar.pop()
            m_user.avatar = avatar.avatar
            m_user.avatar_hash = avatar.avatar_hash
        hist = [h[1] for h in history if h[1].user_id == user.id]
        if hist:
            for h in hist:
                m_history = History()
                m_history.datetime = h.datetime
                m_history.ip = h.ip
                m_user.history.append(m_history)
        m_user.save()


def load_contacts_to_mongo(sqlite, users):
    for user in users:
        m_user = User.objects(name=user.name).first()
        contacts = sqlite.get_contacts(user.name)
        for c in contacts:
            m_contact = User.objects(name=c.name).first()
            if m_contact in m_user.contacts:
                continue
            m_user.contacts.append(m_contact)
        m_user.save()


def load_messages_to_mongo(messages):
    for msg in messages:
        sender, message, recipient = msg[0:3]
        m_sender = User.objects(name=sender.name).first()
        m_recipient = User.objects(name=recipient.name).first()

        m_message = Message()
        m_message.sender = m_sender
        m_message.recipient = m_recipient
        m_message.text = message.text
        m_message.time = message.time
        m_message.save()


def load_room_messages(sqlite, rooms):
    for room in rooms:
        messages = sqlite.get_room_messages(room.name)
        m_room = Room.objects(name=room.name)
        if not m_room:
            m_room = Room()
            m_room.name = room.name
            m_room.save()

        for msg in messages:
            sender, message = msg[0:2]
            m_sender = User.objects(name=sender.name).first()

            m_message = Message()
            m_message.sender = m_sender
            m_message.room = m_room
            m_message.text = message.message
            m_message.time = message.time
            m_message.save()


def import_from_sqlite(sqlite_file=None, mongo_host=None):
    print(f'{sqlite_file if sqlite_file else "SQLite Default"} -> {mongo_host if mongo_host else "Mongo Default"}')

    sqlite = ServerStorage(sqlite_file)
    mongo = ServerStorageMongo(mongo_host)

    s_users = sqlite.get_users()
    s_history = sqlite.get_history()
    s_avatars = sqlite.get_users_avatar()

    print('Move users')
    load_users_to_mongo(s_users, s_history, s_avatars)
    print('-' * 50)
    print('Move contacts')
    load_contacts_to_mongo(sqlite, s_users)
    print('-' * 50)

    s_messages = sqlite.get_user_messages()
    print('Move user messages')
    load_messages_to_mongo(s_messages)
    print('-' * 50)
    s_rooms = sqlite.get_rooms()
    print('Move room messages')
    load_room_messages(sqlite, s_rooms)
    print('-' * 50)


def main():
    argv_len = len(sys.argv)
    sqlite_file = sys.argv[1] if argv_len > 1 else None
    mongo_host = sys.argv[2] if argv_len > 2 else None
    import_from_sqlite(sqlite_file, mongo_host)


if __name__ == '__main__':
    main()
