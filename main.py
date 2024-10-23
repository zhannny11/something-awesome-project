#!/usr/bin/env python3 
import secrets
import string
import sqlite3
import helpers


"""Initialise database"""
def create_table(db_name):
    # Connect to the SQLite database (creates the file if it doesn't exist)
    connection = sqlite3.connect(db_name)

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

    # Commit the changes and close the connection
    connection.commit()
    cursor.close()
    return connection

"""Generates passwords of a provided length"""
def password_gen(password_length):
    characters = string.ascii_letters + string.digits
    secure_password = ''.join(secrets.choice(characters) for i in range(password_length))
    return secure_password

def main():
    try:

        db_name = "password.db"
        db = create_table(db_name)
        cursor = db.cursor()

        url = "https://www.adidas.com.au/"
        username = "zhannny11@gmail.com"
        password = password_gen(8)
        cursor.execute("""
            INSERT INTO passwords (url, username, password)
            VALUES (?, ?, ?)
        """, (url, username, password))

        db.commit()

        # fetch all records
        cursor.execute("select * from passwords")
        record = cursor.fetchall()
        print(record)
        db.commit()

    except Exception as err:
        print(err)
    finally:
        if db:
            db.close()


if __name__ == "__main__":
    main()