import csv
import os
import time
from datetime import datetime as datetime_module
from threading import Thread
import configparser
from typing import Tuple

import adafruit_gps
import pynmea2
import serial

import database

class Gps(Thread):


    def __init__(self, config: configparser.ConfigParser, track: database.Track):
        Thread.__init__(self, name="gps", daemon=True)
        self.config = config
        self.track = track

        self.database_connection = None
        self.gps = None
        self.message_interval = 10
        self.last_message_time = 0


    def run(self):
        self.database_connection = database.Database.connect()
        self.init_gps(self.config['device']['serial'])

        self.wait_for_valid_position()

        while True:
            try:
                nmea, line = self.read_nmea()
                if nmea.is_valid and nmea.sentence_type == "RMC":
                    now = time.monotonic()
                    datetime = datetime_module.combine(nmea.datestamp, nmea.timestamp)
                    timestamp = datetime_module.timestamp(datetime)

                    position = database.Position(timestamp, nmea.latitude, nmea.longitude, nmea.spd_over_grnd * 1.852, self.track.uuid)
                    database.PositionService.insert(self.database_connection, position)
            except AttributeError:
                continue
            except Exception as e:
                print("Error {}".format(e))
                continue
                

    def wait_for_valid_position(self):
        print("waiting GPS fix...")
        while True:
            nmea, _ = self.read_nmea()
            try:
                if nmea and nmea.is_valid:
                    break
            except:
                pass
        print("GPS fix acquired !")
        

    def read_nmea(self) -> Tuple[pynmea2.NMEASentence, str]:
        line = str(self.gps.readline(), "ascii").strip()
        nmea = None
        if line:
            try:
                nmea = pynmea2.parse(line)
            except pynmea2.ParseError:
                pass
        return nmea, line


    def send_command(self, command: str):
        self.gps.send_command(command)
        time.sleep(1)


    def init_gps(self, path: str):
        debug = False

        # open serial GPS
        uart = serial.Serial(path, baudrate=9600, timeout=10)
        self.gps = adafruit_gps.GPS(uart, debug=debug)

        # set baudrate to 115200
        self.send_command(b'PMTK251,115200')

        # re-open serial GPS
        uart = serial.Serial(path, baudrate=115200, timeout=10)
        self.gps = adafruit_gps.GPS(uart, debug=debug)

        # enable only $GPRMC
        self.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        # set update rate to 10 times per seconds
        self.send_command(b'PMTK220,100')
