import os
from base64 import b64encode, b64decode

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES


LENGTH = 1024


def gen_keys():
    pr_key = RSA.generate(LENGTH)
    pub_key = pr_key.publickey()
    return pr_key, pub_key


def import_pub_key(binary_key):
    return RSA.import_key(binary_key)


def encrypt_rsa(pub_key, data):
    if not isinstance(data, bytes):
        data = data.encode()
    encrytopr = PKCS1_OAEP.new(pub_key)
    encrypt = encrytopr.encrypt(data)
    return b64encode(encrypt)


def decrypt_rsa(prv_key, data):
    enc = b64decode(data)
    decryptor = PKCS1_OAEP.new(prv_key)
    return decryptor.decrypt(enc)


class ClientCrypt:
    CRYPT_MODE = AES.MODE_CBC
    __slots__ = ('secret',)

    def __init__(self, secret):
        self.secret = secret

    @classmethod
    def gen_secret(cls, user, contact):
        user = user.encode()
        contact = contact.encode()
        salt = os.urandom(16 * (max(len(user), len(contact)) // 16 + 1))
        key = bytes([(u + c) % 256 for u, c in zip(user, contact)])
        key = bytes([(k + s) % 256 for k, s in zip(cls.__padding(key), salt)])
        return cls(key)

    @staticmethod
    def __padding(text):
        return text + b" " * (16 - len(text) % 16)

    def encript_msg(self, message):
        aes_encryptor = AES.new(self.secret, self.CRYPT_MODE)
        return b64encode(aes_encryptor.iv + aes_encryptor.encrypt(self.__padding(message)))

    def decrypt_msg(self, message):
        message = b64decode(message)
        aes_encryptor = AES.new(self.secret, self.CRYPT_MODE, iv=message[:16])
        return aes_encryptor.decrypt(message[16:]).strip()
