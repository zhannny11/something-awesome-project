#!/usr/bin/env python3 
import secrets
import string
import sqlite3
import bcrypt
import getpass
import argparse
import sys
import master_password
import base64
from pbkdf2 import PBKDF2
from Crypto.Cipher import AES

"""Encrypt a password using AES."""
def encrypt_password(password_to_encrypt, master_password_hash, salt):
    key = PBKDF2(str(master_password_hash), salt).read(32)
    data_convert = str.encode(password_to_encrypt)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data_convert)
    # Concatenate the nonce and tag with the ciphertext
    add_nonce_tag = cipher.nonce + tag + ciphertext
    encoded_ciphertext = base64.b64encode(add_nonce_tag).decode()
    return encoded_ciphertext

"""Decrypt a password using AES."""
def decrypt_password(password_to_decrypt, master_password_hash, salt):
    if len(password_to_decrypt) % 4:
        password_to_decrypt += '=' * (4 - len(password_to_decrypt) % 4)
    convert = base64.b64decode(password_to_decrypt)
    key = PBKDF2(str(master_password_hash), salt).read(32)
    # Extract the nonce, tag, and ciphertext from the decoded data
    nonce = convert[:16]
    tag = convert[16:32]
    ciphertext = convert[32:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

    try:
        plaintext = cipher.decrypt_and_verify(ciphertext, tag).decode()
    except ValueError as e:
        print(f"Decryption failed: {e}")
        return None

    return plaintext

"""Initialise database"""
def create_table(db_name):
    try:
        # Connect to the SQLite database (creates the file if it doesn't exist)
        connection = sqlite3.connect(db_name)
        print(f"Successfully connected to the database: {db_name}")

        # Create a cursor object
        cursor = connection.cursor()

        # Create the table
        cursor.execute("""
            create table if not exists passwords (
                id integer primary key,
                url text not null,
                username text not null,
                password text not null
            );
        """)
        connection.commit()

        cursor.execute("""
            create table if not exists master_password (
                id integer primary key,
                password_hash text not null,
                salt text not null
            );
        """)

        connection.commit()
        return connection, cursor  # Return both connection and cursor
    except sqlite3.Error as e:
        print(f"Error creating database or tables: {e}")
        return None, None  # Return None if there was an error


def add_entry(cursor, url, username, hashed_password):
    cursor.execute("insert into passwords (url, username, password) VALUES (?, ?, ?)", (url, username, hashed_password))
    print(f"Record Added:\n url: {url}, Username: {username}, Encrypted: {hashed_password}")

def query_entry(cursor, url, db_name):
    cursor.execute("select * from passwords where url = ?", (url,))
    record = cursor.fetchone()

    if record:
        encrypted_password = record[3]  # Assuming the password is in the fourth column
        print("encrypted_password", encrypted_password)
        stored_hash, salt = master_password.retrieve_master_password(db_name)
        decrypted_password = decrypt_password(encrypted_password, stored_hash, salt)
        if decrypted_password is not None:  # Check if decryption was successful
            print(f"Record: URL: {record[1]}, Username: {record[2]}, Password: {decrypted_password}")
            print(f"Record With Encrypted Password: URL: {record[1]}, Username: {record[2]}, Password: {record[3]}")
        else:
            print("Failed to decrypt the password.")
    else:
        print(f"Could not find record matching the value of '{url}'")



"""Generates passwords of a provided length"""
def password_gen(password_length):
    characters = string.ascii_letters + string.digits
    secure_password = ''.join(secrets.choice(characters) for i in range(password_length))
    return secure_password

"""Initialises parser and respective arguments"""
def initialise_parser():
    # Initialise parser
    my_parser = argparse.ArgumentParser(description="Password Manager Vault: Add, Update, and Delete urls, Usernames, and Passwords",     
                                        usage="%(prog)s [-a url USERNAME] [-q url] [-l] [-d url] [-ap url USERNAME PASSWORD] ... ")
    # Define command line arguments
    my_parser.add_argument("-a", "--add", type=str, nargs=2, help="Add new entry", metavar=("[url]", "[USERNAME]"))
    my_parser.add_argument("-q", "--query", type=str, nargs = 1, help="Look up entry by url", metavar=("[url]"))
    my_parser.add_argument("-l", "--list", action="store_true", help="List all entries in password vault")
    my_parser.add_argument("-d", "--delete", type=str, nargs=1, help="Delete entry by url", metavar=("[url]")) 
        # If users wish to add their own password instead of having an autogenerated one
    my_parser.add_argument("-ap", "--add_password", type=str, nargs=3, help="Add manual password", metavar=("[url]", "[USERNAME]", "[PASSWORD]")) 
    my_parser.add_argument("-uurl", "--update_url", type=str, nargs=2, help="Update a url", metavar=("[NEW_url]", "[OLD_url]"))
    my_parser.add_argument("-uname", "--update_username", type=str, nargs=2, help="Update a username in account", metavar=("[url]", "[NEW_USERNAME]")) 
    my_parser.add_argument("-upasswd", "--update_password", type=str, nargs=2, help="Update a password in account", metavar=("[url]", "[NEW_PASSWORD]"))

    return my_parser

def main():
    db_name = "/app/data/password.db"
    connection, cursor = create_table(db_name)  # Get both connection and cursor

    if connection is None or cursor is None:
        print("Failed to connect to the database. Exiting...")
        return  # Exit if there was an error
    try:        
        # Prompt for the master password
        master_password_input = getpass.getpass("Master password: ")
        # wish to set up 2fa with google authenticator but for the time beign set a fixed plaintext password
        second_FA_location = "i like trains"

        # Hash the master password
        master_password_hash = master_password.hash_master_password(master_password_input + second_FA_location)
       # Check if a master password exists in the database
        stored_hash = cursor.execute("select password_hash from master_password").fetchone()
        if stored_hash is None:
            salt = master_password.gen_salt()
            cursor.execute("insert into master_password (password_hash, salt) values (?, ?)", (master_password_hash, salt))
            connection.commit()
            print("Master password saved successfully.")

        else:
            if not master_password.verify_password(master_password_input + second_FA_location, stored_hash[0]):
                print("Failed to authenticate. ")
                sys.exit()

            print("Master password authenticated successfully.")

        args = initialise_parser().parse_args()


        if args.add:
            url, username = args.add
            # Check if the URL already exists
            cursor.execute("select * from passwords where trim(lower(url)) = trim(lower(?))", (url,))
            existing_entry = cursor.fetchone()

            if existing_entry:
                print(f"An entry for URL '{url}' already exists. Exiting without adding a new entry.")
                sys.exit()  # Exit early if URL already exists

            password = password_gen(12)
            stored_hash, salt = master_password.retrieve_master_password(db_name)
            hashed_password = encrypt_password(password, stored_hash, salt)
            add_entry(cursor, url, username, hashed_password)
            connection.commit()
        elif args.query:
            url = args.query[0]
            query_entry(cursor, url, db_name)
        elif args.list:
            cursor.execute("select * from passwords")
            records = cursor.fetchall()
            if records:
                for i, entry in enumerate(records, start=1):
                    url = entry[1]
                    username = entry[2]
                    encrypted_password = entry[3]
                    stored_hash, salt = master_password.retrieve_master_password(db_name)
                    decrypted_password = decrypt_password(encrypted_password, stored_hash, salt)
                    if decrypted_password is not None:  # Ensure decryption was successful
                        print(f"Entry #{i}: URL: {url}, Username: {username}, Password: {decrypted_password}")
                    else:
                        print(f"Entry #{i}: URL: {url}, Username: {username}, Password: (decryption failed)")
            else:
                print("No entries found in the password manager.")
        elif args.delete:
            url = args.delete[0]
            cursor.execute("select * from passwords where trim(lower(url)) = trim(lower(?))", (url,))
            record = cursor.fetchone()
            if record:
                # Proceed with deletion
                cursor.execute("delete from passwords where trim(lower(url)) = trim(lower(?))", (url,))
                connection.commit()
                print(f"Deleted entry for url: {url}")
                # Check if the deletion was successful
                cursor.execute("SELECT * FROM passwords WHERE trim(lower(url)) = trim(lower(?))", (url,))
                if cursor.fetchone():
                    print(f"Deletion failed, entry for URL '{url}' still exists.")
                else:
                    print(f"Successfully deleted entry for URL '{url}'.")
            else:
                print(f"No entry found for URL: {url}.")

        elif args.add_password:
            url, username, password = args.add_password
            stored_hash, salt = master_password.retrieve_master_password(db_name)
            encrypted_password = encrypt_password(password, stored_hash, salt)
            add_entry(cursor, url, username, encrypted_password)
            connection.commit()
            print(f"Password added for entry")
        elif args.update_url:
            new_url, old_url = args.update_url
            cursor.execute("update passwords set url = ? where url = ?", (new_url, old_url))
            connection.commit()
            print(f"Updated url from {old_url} to {new_url}.")
        elif args.update_username:
            url, new_username = args.update_username
            cursor.execute("update passwords set username = ? where url = ?", (new_username, url))
            connection.commit()
            print(f"Updated username for URL: {url}.")
        elif args.update_password:
            url, new_password = args.update_password
            stored_hash, salt = master_password.retrieve_master_password(db_name)
            encrypted_password = encrypt_password(new_password, stored_hash, salt)
            cursor.execute("update passwords set password = ? where url = ?", (encrypted_password, url))
            connection.commit()
            print(f"Updated password for URL: {url}.")
        connection.commit()
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
    except Exception as err:
        print(err)
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()