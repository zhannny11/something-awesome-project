import hashlib
from hashlib import sha256
import base64
from base64 import b64encode, b64decode
import os

"""Generate a random salt."""
def gen_salt(length=16):
    return os.urandom(length)

"""Hash the master password using PBKDF2."""
def hash_password(master_password, salt, iterations=100000):
    dk = hashlib.pbkdf2_hmac('sha256', master_password.encode(), salt, iterations)
    return base64.b64encode(dk).decode()

"""Verify the provided password against the stored hash."""
def verify_password(stored_hash, provided_password, salt):
    hash_to_check = hash_password(provided_password, salt)
    return hash_to_check == stored_hash
