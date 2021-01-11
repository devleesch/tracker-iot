import configparser
import os
import time
from datetime import datetime as datetime_module
from threading import Thread
import uuid

import adafruit_gps
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
                    nmea, _ = self.read_nmea()
                    datetime = datetime_module.combine(nmea.datestamp, nmea.timestamp)
                    todayStr = datetime.isoformat()
                    f = open('csv/'+todayStr+'.csv', 'w')
                except:
                    continue
            print('csv/'+todayStr+'.csv created !')

        last_timestamp_sent = -self.config.getfloat('device', 'interval')
        while True:
            try:
                line = self.read_nmea()
                if line:
                    timestamp = time.monotonic()

                    if timestamp - last_timestamp_sent >= self.config.getfloat('device', 'interval'):
                        database.QueueService.insert(self.database_connection, model.Message(uuid.uuid4(),))
                        last_timestamp_sent = timestamp

                    if self.config.getboolean('device', 'track_mode'):
                        f.write(f"{line}\n")
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
        

    def read_nmea(self) -> str:
        return str(self.gps.readline(), "ascii").strip()


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
