from os import sendfile
import sqlite3
import model


class Database:
    @staticmethod
    def connect() -> sqlite3.Connection:
        return sqlite3.connect("tracker.db")


    @staticmethod
    def init():
        conn = Database.connect()
        conn.executescript("""
            create table if not exists positions(
                timestamp REAL NOT NULL PRIMARY KEY,
                latitude TEXT,
                longitude TEXT,
                speed TEXT
            );
        """)
        conn.close()


class PositionService:
    @staticmethod
    def insert(conn: sqlite3.Connection, position: model.Position):
        conn.execute("""
            insert into positions 
            values(?, ?, ?, ?)""", [
                position.timestamp,
                str(position.latitude),
                str(position.longitude),
                str(position.speed)
        ])
        conn.commit()

    
    @staticmethod
    def select_all(conn: sqlite3.Connection):
        values = []
        for row in conn.execute("""
                select timestamp, latitude, longitude, speed
                from positions
            """):
            values.append(model.Position(row[0], row[1], row[2], row[3]))
        return values


    @staticmethod
    def delete(conn: sqlite3.Connection, position: model.Position):
        conn.execute("""
            delete from positions 
            where timestamp = ?""", [
                position.timestamp
        ])
        conn.commit()