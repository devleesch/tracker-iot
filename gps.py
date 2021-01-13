from datetime import datetime as datetime_module
from threading import Thread
import tracker
import os
import time
import uuid

import adafruit_gps
import serial
import pynmea2

import config
import database
import model


class Gps(Thread):
    def __init__(self):
        Thread.__init__(self, name="gps", daemon=True)
        self.database_connection = None
        self.gps = None
        self.stop = False

    def wait_for_valid_position(self):
        print("waiting GPS fix...")
        while True:
            nmea = Gps.parse_nmea(self.read_nmea())
            try:
                if nmea and nmea.is_valid:
                    break
            except:
                pass
        print("GPS fix acquired !")
        
    def read_nmea(self) -> str:
        return str(self.gps.readline(), "ascii").strip()

    def send_command(self, command: str):
        self.gps.send_command(command)
        time.sleep(1)

    def init_gps(self):
        debug = False

        # open serial GPS
        uart = serial.Serial(config.parser.get('device', 'serial'), baudrate=9600, timeout=10)
        self.gps = adafruit_gps.GPS(uart, debug=debug)

        # set baudrate to 115200
        self.send_command(b'PMTK251,115200')

        # re-open serial GPS
        uart = serial.Serial(config.parser.get('device', 'serial'), baudrate=115200, timeout=10)
        self.gps = adafruit_gps.GPS(uart, debug=debug)

        # enable only $GPRMC
        self.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        # set update rate to 10 times per seconds
        self.send_command(b'PMTK220,100')

    @staticmethod
    def parse_nmea(line: str):
        if line:
            try:
                return pynmea2.parse(line)
            except pynmea2.ParseError:
                pass
        return None

class GpsTrack(Gps):
    def run(self):
        self.database_connection = database.Database.connect()
        self.init_gps()
        self.wait_for_valid_position()

        f = self.create_track_file()
        while True:
            try:
                line = self.read_nmea()
                if line and line.startswith("$GPRMC"):
                    f.write(f"{line}\n")
                    f.flush()
            except Exception as e:
                print("GpsTrack.run() error : {}".format(e))
                pass

            if self.stop:
                break
        print("GpsTrack.run() ended !")

    def create_track_file(self):
        f = None
        if config.parser.getboolean('device', 'track_mode'):
            # create directory to store csv
            try:
                os.mkdir("csv/")
            except FileExistsError:
                pass

            # open file for csv
            todayStr = None
            while not todayStr:
                try:
                    nmea = Gps.parse_nmea(self.read_nmea())
                    datetime = datetime_module.combine(nmea.datestamp, nmea.timestamp)
                    todayStr = datetime.isoformat()
                    f = open('csv/'+todayStr+'.csv', 'w')
                except:
                    continue
            print('csv/'+todayStr+'.csv created !')
        return f


class GpsRoad(Gps):
    def run(self):
        self.database_connection = database.Database.connect()
        self.init_gps()

        self.wait_for_valid_position()

        last_timestamp_sent = -config.parser.getfloat('device', 'interval')
        while True:
            try:
                line = self.read_nmea()
                if line and line.startswith("$GPRMC"):
                    timestamp = time.monotonic()
                    if timestamp - last_timestamp_sent >= config.parser.getfloat('device', 'interval'):
                        database.QueueService.insert(self.database_connection, model.Message(str(uuid.uuid4()), line))
                        last_timestamp_sent = timestamp
                    time.sleep(1)
            except Exception as e:
                print("GpsRoad.run() error : {}".format(e))
                pass

            if self.stop:
                break
        print("GpsRoad.run() ended !")
