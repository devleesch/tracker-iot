from os import sendfile
import sqlite3
from sqlite3.dbapi2 import Cursor
import uuid
import datetime

from pynmea2.nmea_utils import timestamp

class Database:
    @staticmethod
    def init():
        conn = sqlite3.connect("tracker.sqlite")
        cur = conn.cursor()
        cur.executescript("""
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
        cur.close()
        conn.close()


class Track:
    def __init__(self, uuid = uuid.uuid4(), start_time = datetime.datetime.now()) -> None:
        self.uuid = uuid
        self.start_time = start_time


class TrackServive:
    @staticmethod
    def insert(conn: sqlite3.Connection, track: Track):
        conn.execute("insert into track values(?, ?)", [str(track.uuid), str(track.start_time)])
        conn.commit()

    @staticmethod
    def selectall(conn: sqlite3.Connection):
        values = []
        for row in conn.execute("select * from track"):
            values.append(row)
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
        conn.execute("insert into Position(?, ?, ?, ?, ?, ?)")
        conn.commit()


Database.init()

conn = sqlite3.connect("tracker.sqlite")
TrackServive.insert(conn, Track())
for t in TrackServive.selectall(conn):
    print(t)
conn.close()

