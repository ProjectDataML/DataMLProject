import sqlite3
from sqlite3 import Connection

def create_connection(path: str) -> Connection:
    return sqlite3.connect(path)

def execute_query(connection: Connection, query: str):
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()

def batch_insert(connection: Connection, query: str, data):
    cursor = connection.cursor()
    cursor.executemany(query, data)
    connection.commit()