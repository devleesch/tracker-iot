import configparser
import csv
import os
import time
from datetime import datetime as datetime_module
from threading import Thread
from typing import Tuple

import adafruit_gps
import pynmea2
import serial

import database
import model


class Gps(Thread):
    def __init__(self, config: configparser.ConfigParser):
        Thread.__init__(self, name="gps", daemon=True)
        self.config = config

        self.database_connection = None
        self.gps = None


    def run(self):
        self.database_connection = database.Database.connect()
        self.init_gps(self.config['device']['serial'])

        self.wait_for_valid_position()

        f = None
        writer = None
        if self.config.getboolean('device', 'track_mode'):
            # create directory to store csv
            try:
                os.mkdir("csv/")
            except FileExistsError:
                pass

            # open file for csv
            todayStr = None
            while not todayStr:
                try:
                    nmea, line = self.read_nmea()
                    print(nmea, line)
                    datetime = datetime_module.combine(nmea.datestamp, nmea.timestamp)
                    todayStr = datetime.isoformat()
                    f = open('csv/'+todayStr+'.csv', 'w')
                    writer = csv.writer(f, delimiter=';')
                except:
                    continue
            print('csv/'+todayStr+'.csv created !')

        last_timestamp_sent = 0
        while True:
            try:
                nmea, line = self.read_nmea()
                if nmea.is_valid and nmea.sentence_type == "RMC":
                    datetime = datetime_module.combine(nmea.datestamp, nmea.timestamp)
                    timestamp = datetime_module.timestamp(datetime)

                    position = model.Position(timestamp, nmea.latitude, nmea.longitude, nmea.spd_over_grnd * 1.852)
                    if timestamp - last_timestamp_sent >= self.config.getfloat('device', 'interval'):
                        database.PositionService.insert(self.database_connection, position)
                        last_timestamp_sent = timestamp

                    if self.config.getboolean('device', 'track_mode'):
                        writer.writerow([position.timestamp, position.latitude, position.longitude, position.speed])
                        f.flush()
            except Exception as e:
                print("Exception : {}".format(e))
                pass
                

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
