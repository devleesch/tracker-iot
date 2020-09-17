from os import sendfile
import sqlite3
from sqlite3.dbapi2 import Cursor
import uuid
import datetime

class Database:
    @staticmethod
    def connect() -> sqlite3.Connection:
        return sqlite3.connect("tracker.db")


    @staticmethod
    def init():
        conn = Database.connect()
        conn.executescript("""
            create table if not exists track(
                uuid TEXT NOT NULL PRIMARY KEY,
                start_time TEXT
            );

            create table if not exists positions(
                timestamp REAL NOT NULL PRIMARY KEY,
                latitude TEXT,
                longitude TEXT,
                speed TEXT,
                track_uuid TEXT,
                FOREIGN KEY(track_uuid) REFERENCES track(uuid),
            );

            create index if not exists positions__track_uuid__idx on positions(track_uuid);
        """)
        conn.close()


class Track:
    def __init__(self, uuid = uuid.uuid4(), start_time = datetime.datetime.now()) -> None:
        self.uuid = uuid
        self.start_time = start_time


class TrackServive:
    @staticmethod
    def insert(conn: sqlite3.Connection, track: Track):
        conn.execute("""
        insert into track 
        values(?, ?)
        """, [
            str(track.uuid), 
            str(track.start_time)
        ])
        conn.commit()

    @staticmethod
    def select_all(conn: sqlite3.Connection):
        values = []
        for row in conn.execute("""
            select uuid, start_time
            from track
            """):
            values.append(Track(row[0], row[1]))
        return values

class Position:
    def __init__(self, timestamp, latitude, longitude, speed, track_uuid, processed = False, sent = False) -> None:
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude
        self.speed = speed
        self.track_uuid = track_uuid


class PositionService:
    @staticmethod
    def insert(conn: sqlite3.Connection, position: Position):
        conn.execute("""
            insert into positions 
            values(?, ?, ?, ?, ?)""", [
                position.timestamp,
                str(position.latitude),
                str(position.longitude),
                str(position.speed),
                str(position.track_uuid)
        ])
        conn.commit()

    
    @staticmethod
    def select_all(conn: sqlite3.Connection):
        values = []
        for row in conn.execute("""
                select timestamp, latitude, longitude, speed, track_uuid
                from positions
            """):
            values.append(Position(row[0], row[1], row[2], row[3], row[4]))
        return values

    @staticmethod
    def delete(conn: sqlite3.Connection, position: Position):
        conn.execute("""
            delete from positions 
            where timestamp = ?""", [
                position.timestamp
        ])
        conn.commit()