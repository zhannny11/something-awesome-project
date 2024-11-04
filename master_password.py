import os
import bcrypt
import sqlite3

"""Generate a random salt."""
def gen_salt(length=16):
    return os.urandom(length)

"""Hashes the master password using bcrypt."""
def hash_master_password(master_password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(master_password.encode(), salt)
    return hashed_password.decode(), salt.decode()

"""Verify the provided password against the stored hash."""
def verify_password(provided_password):
    with sqlite3.connect("/app/data/password.db") as conn:
        cursor = conn.cursor()
        # there's only one entry
        cursor.execute("select password_hash, salt from master_password WHERE id = 1")
        result = cursor.fetchone()
        if result:
            stored_hash, salt = result
            # Hash the input password with the retrieved salt and compare
            return bcrypt.checkpw(input_password.encode(), stored_hash)
        else:
            return False

"""Retrieve the master password from the database."""
def retrieve_master_password(db_name):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        # there's only one entry
        cursor.execute("select password_hash, salt from master_password WHERE id = 1")
        result = cursor.fetchone()
        print("result: ", result)

        if result:
            stored_hash, salt = result
            return stored_hash, salt
        else:
            print("No master password found. Please set up a master password first.")
            return None, None  # Return None if no master password exists
