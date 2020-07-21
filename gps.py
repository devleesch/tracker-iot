import csv
import os
import sys
import time
from datetime import datetime as datetime_module
from threading import Thread
import configparser
import platform
from typing import Tuple

import adafruit_gps
import pynmea2
import serial
from persistqueue import FIFOSQLiteQueue

import message
import tracker

class Gps(Thread):

    def __init__(self, config: configparser.ConfigParser, queue: FIFOSQLiteQueue):
        Thread.__init__(self, name="gps", daemon=True)
        self.config = config
        self.queue = queue

        self.gps = None

        self.message_interval = 10
        self.last_message_time = -self.message_interval

        self.f = None
        self.writer = None

    def run(self):

        self.init_gps(self.config['device']['serial'])

        self.wait_for_valid_position()
        self.update_system_datetime()

        if self.config['device'].getboolean('track_mode'):
            # create directory to store csv
            try:
                os.mkdir("csv/")
            except FileExistsError:
                print('csv/ directory already exist')

            # open file for csv
            todayStr = datetime_module.now().isoformat()
            self.f = open('csv/'+todayStr+'.csv', 'w')
            self.writer = csv.writer(self.f)

        while True:
            try:
                nmea, line = self.read_nmea()
                if nmea.is_valid and nmea.sentence_type == "RMC":
                    now = time.monotonic()
                    datetime = datetime_module.combine(nmea.datestamp, nmea.timestamp)
                    timestamp = datetime_module.timestamp(datetime)
                    
                    self.track_mode_write(timestamp, nmea)
                    self.queue_message(now, line)
            except AttributeError:
                continue
                


    def wait_for_valid_position(self):
        print("waiting GPS fix...")
        while True:
            nmea, _ = self.read_nmea()
            try:
                if nmea and nmea.is_valid:
                    # start new line for next log line
                    print("")
                    break
                    time.sleep(1)
            except:
                pass
        print("GPS fix acquired !")
        

    def read_nmea(self) -> Tuple[pynmea2.NMEASentence, str]:
        line = str(self.gps.readline(), "ascii").strip()
        print("read_nmea: {}".format(line))
        nmea = None
        if line:
            try:
                nmea = pynmea2.parse(line)
            except pynmea2.ParseError:
                pass
        print("read_nmea: {}, {}".format(nmea, line))
        return nmea, line


    def track_mode_write(self, timestamp, nmea):
        if self.config['device'].getboolean('track_mode'):
            try:
                # write to csv for track
                self.writer.writerow([timestamp, nmea.latitude, nmea.longitude, nmea.spd_over_grnd * 1.852])
                self.f.flush()
            except Exception as e:
                print("Error writing to csv !", e)


    def queue_message(self, now, line):
        if now - self.last_message_time >= self.message_interval:
            self.last_message_time = now
            msg = message.Message(self.config['device']['id'], line)
            self.queue.put(msg.to_json())

    
    def update_system_datetime(self):
        # get date from GPS
        nmea = None
        while not nmea:
            nmea, _ = self.read_nmea()
            print(nmea)

        now = datetime_module.combine(nmea.datestamp, nmea.timestamp)

        # get system date
        pipe = os.popen("date -u +\"%Y-%m-%d %H:%M:%S\"")
        os_date = datetime_module.fromisoformat(pipe.read().rstrip("\n"))

        # compute delta between GPS and OS date
        delta = abs((now - os_date))
        print("os_date: {}; gps_date: {}; delta: {}".format(os_date, now, delta))
        if delta.total_seconds() >= 60:
            print("updating system datetime")
            if platform.system() == "Linux":
                print("set system time to {}".format(now))
                #os.system("date -u +\"%Y-%m-%d %H:%M:%S\"")
            else:
                print("OS not supported")


    def send_command(self, command: str):
        self.gps.send_command(command)
        time.sleep(1)


    def init_gps(self, path: str):
        debug = True

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
