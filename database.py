import sqlite3
from uuid import uuid4
import model
import unittest


class Database:
    @staticmethod
    def connect() -> sqlite3.Connection:
        return sqlite3.connect("tracker.db")


    @staticmethod
    def init():
        conn = Database.connect()
        conn.executescript("""
            create table if not exists queue(
                uuid TEXT NOT NULL PRIMARY KEY,
                value TEXT
            );
        """)
        conn.close()


class QueueService:
    @staticmethod
    def insert(conn: sqlite3.Connection, message: model.Message):
        conn.execute("""
            insert into queue 
            values(?, ?)""", [
                message.uuid,
                message.value
        ])
        conn.commit()

    
    @staticmethod
    def select_all(conn: sqlite3.Connection):
        values = []
        for row in conn.execute("""
                select uuid, value
                from queue
            """):
            values.append(model.Message(row[0], row[1]))
        return values


    @staticmethod
    def delete(conn: sqlite3.Connection, message: model.Message):
        conn.execute("""
            delete from queue 
            where uuid = ?""", [
                message.uuid
        ])
        conn.commit()


class InsertTest(unittest.TestCase):
    def test_loop(self):
        connect = Database.connect()
        trip = str(uuid4())
        for i in range(1000):
            QueueService.insert(connect, model.Message(str(uuid4()), i, trip))
        connect.close()

if __name__ == '__main__':
    unittest.main()