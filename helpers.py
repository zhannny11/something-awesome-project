#!/usr/bin/env python3 

# mainly used for sql statements
def insert_db_row():
    insert_query = """INSERT INTO Vault (URL, USRNAME, PASSWD) VALUES (%s, %s,%s)"""
    return insert_query 