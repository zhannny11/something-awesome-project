import os
import bcrypt
import sqlite3
import base64


"""Generate a random salt."""
def gen_salt(length=16):
    salt_bytes = os.urandom(length)
    return base64.b64encode(salt_bytes).decode('utf-8')

"""Hashes the master password using bcrypt."""
def hash_master_password(master_password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(master_password.encode(), salt)
    return hashed_password.decode()

"""Verify the provided password against the stored hash."""
def verify_password(provided_password, stored_password_hash):
    if stored_password_hash is None or not isinstance(stored_password_hash, str):
        return False

    # Verify the password using bcrypt
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password_hash.encode('utf-8'))

"""Retrieve the master password from the database."""
def retrieve_master_password(db_name):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        # there's only one entry
        cursor.execute("select password_hash, salt from master_password where id = 1")
        result = cursor.fetchone()

        if result:
            stored_hash, salt = result
            return stored_hash, salt
        else:
            print("No master password found. Please set up a master password first.")
            return None, None  # Return None if no master password exists
