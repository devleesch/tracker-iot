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
                sent BOOLEAN,
                FOREIGN KEY(track_uuid) REFERENCES track(uuid)
            );
        """)
        conn.close()


class Track:
    def __init__(self, uuid = uuid.uuid4(), start_time = datetime.datetime.now()) -> None:
        self.uuid = uuid
        self.start_time = start_time


class TrackServive:
    @staticmethod
    def insert(conn: sqlite3.Connection, track: Track):
        conn.execute("insert into track values(?, ?)", [
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
    def __init__(self, timestamp, latitude, longitude, speed, track_uuid, sent = False) -> None:
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude
        self.speed = speed
        self.track_uuid = track_uuid
        self.sent = sent


class PositionService:
    @staticmethod
    def insert(conn: sqlite3.Connection, position: Position):
        conn.execute("""
            insert into positions 
            values(?, ?, ?, ?, ?, ?)""", [
                position.timestamp,
                str(position.latitude),
                str(position.longitude),
                str(position.speed),
                str(position.track_uuid),
                position.sent
        ])
        conn.commit()

    
    @staticmethod
    def select_all_not_sent(conn: sqlite3.Connection):
        values = []
        for row in conn.execute("""
                select timestamp, latitude, longitude, speed, track_uuid, sent
                from positions 
                where sent = 0
            """):
            values.append(Position(row[0], row[1], row[2], row[3], row[4], row[5]))
        return values

    @staticmethod
    def update_sent_by_timestamp(conn: sqlite3.Connection, timestamp: float):
        conn.execute("""
            update positions 
            set sent = 1 
            where timestamp = ?""", [
                timestamp
        ])
        conn.commit()

if __name__ == "__main__":
    Database.init()

    conn = sqlite3.connect("tracker.db")
    TrackServive.insert(conn, Track())
    track_uuid = None
    for t in TrackServive.select_all(conn):
        track_uuid = t[0]
        print(track_uuid)

    PositionService.insert(conn, Position(datetime.datetime.now().timestamp(), 48.67578, 4.867867876, 56, track_uuid))

    conn.close()