#!/usr/bin/env python3 
import secrets
import string
import sqlite3
import helpers
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
    # Concatenate the nonce with the ciphertext
    add_nonce = ciphertext + cipher.nonce
    encoded_ciphertext = base64.b64encode(add_nonce).decode()
    return encoded_ciphertext

"""Decrypt a password using AES."""
def decrypt_password(password_to_decrypt, master_password_hash, salt):
    print("password_to_decrypt", password_to_decrypt)
    if len(password_to_decrypt) % 4:
        password_to_decrypt += '=' * (4 - len(password_to_decrypt) % 4)
    convert = base64.b64decode(password_to_decrypt)
    key = PBKDF2(str(master_password_hash), salt).read(32)
    nonce = convert[-16:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

    try:
        plaintext = cipher.decrypt(convert[:-16]).decode()
    except Exception as e:
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
                salt blob
            );
        """)

        connection.commit()
        # Check if tables exist in the database
        # cursor.execute("select name from sqlite_master where type='table';")
        # tables = cursor.fetchall()
        # if tables:
        #     print("Tables exist:", [table[0] for table in tables])
        # else:
        #     print("No tables")
        return connection, cursor  # Return both connection and cursor
    except sqlite3.Error as e:
        print(f"Error creating database or tables: {e}")
        return None, None  # Return None if there was an error


def add_entry(cursor, url, username, hashed_password):
    cursor.execute("insert into passwords (url, username, password) VALUES (?, ?, ?);", (url, username, hashed_password))
    print(f"Record Added:\n url: {url}, Username: {username}, Encrypted: {hashed_password}")

def query_entry(cursor, url):
    cursor.execute("select * from passwords where url = ?", (url,))
    record = cursor.fetchone()

    if record:
        password_field = record[3]  # Assuming the password is in the fourth column
        decrypted_password = decrypt_password(password_field, master_password_hash, master_password.gen_salt())
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
        # wish to set up 2fa with google authenticator but for the time 
        second_FA_location = "Dee Boo Dah".encode()

        # Hash the master password
        master_password_hash = master_password.hash_password(master_password_input, master_password.gen_salt())
        stored_hash = cursor.execute("SELECT password_hash FROM master_password").fetchone()
        
        # If there's no stored password, save the hash
        if not stored_hash:
            hashed_password = master_password.hash_password(master_password_input, master_password.gen_salt())
            cursor.execute("insert into master_password (password_hash) VALUES (?)", (hashed_password,))
            connection.commit()
            print("Master password saved successfully.")
        elif not master_password.verify_password(stored_hash[0], master_password_input, master_password.gen_salt()):
            print("Failed to authenticate.")
            sys.exit()

        args = initialise_parser().parse_args()


        if args.add:
            url, username = args.add
            password = password_gen(12)
            hashed_password = encrypt_password(password, master_password_hash, master_password.gen_salt())
            add_entry(cursor, url, username, hashed_password)
            connection.commit()
        elif args.query:
            url = args.query[0]
            query_entry(cursor, url)
        elif args.list:
            cursor.execute("SELECT * FROM passwords;")
            records = cursor.fetchall()
            if records:
                for i, entry in enumerate(records, start=1):
                    url = entry[1]
                    username = entry[2]
                    encrypted_password = entry[3]
                    decrypted_password = decrypt_password(encrypted_password, master_password_hash, master_password.gen_salt())
                    print("decrypted password:", decrypted_password)
                    if decrypted_password is not None:  # Ensure decryption was successful
                        print(f"Entry #{i}: URL: {url}, Username: {username}, Password: {decrypted_password}")
                    else:
                        print(f"Entry #{i}: URL: {url}, Username: {username}, Password: (decryption failed)")
            else:
                print("No entries found in the password manager.")
        elif args.delete:
            url = args.delete[0]
            print(f"Trying to delete URL: '{url}'")  # Debugging output
            # TODO: need to fix 
            cursor.execute("select * from passwords where TRIM(LOWER(url)) = TRIM(LOWER(?))", (url,))
            record = cursor.fetchone()
            if record:
                # Proceed with deletion
                cursor.execute("delete from passwords where TRIM(LOWER(url)) = TRIM(LOWER(?))", (url,))
                connection.commit()
                print(f"Deleted entry for url: {url}")

                # Check if the deletion was successful
                cursor.execute("SELECT * FROM passwords WHERE TRIM(LOWER(url)) = TRIM(LOWER(?))", (url,))
                if cursor.fetchone():
                    print(f"Deletion failed, entry for URL '{url}' still exists.")
                else:
                    print(f"Successfully deleted entry for URL '{url}'.")
            else:
                print(f"No entry found for URL: {url}.")

        elif args.add_password:
            url, username, password = args.add_password
            add_entry(cursor, url, username, password)
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
            cursor.execute("update passwords set password = ? where url = ?", (new_password, url))
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