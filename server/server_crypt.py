""" Module implements cryptography on server side """

import binascii
import hashlib
from base64 import b64decode

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


LENGTH = 1024
HASH_METHOD = 'sha256'


def gen_keys():
    """ Function generate public and private keys """

    pr_key = RSA.generate(LENGTH)
    pub_key = pr_key.publickey()
    return pr_key, pub_key


def decrypt_password(pr_key, enc_password):
    """ Function of password decrypt """

    enc = b64decode(enc_password)
    decrytopr = PKCS1_OAEP.new(pr_key)
    return decrytopr.decrypt(enc)


def get_hash_password(password: bytes, username: bytes):
    """ Function returns password hash """

    return binascii.hexlify(hashlib.pbkdf2_hmac(HASH_METHOD, password, username, 100000))
