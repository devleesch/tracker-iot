import csv
import os
import sys
import time
from datetime import datetime as datetime_module
from threading import Thread
import configparser

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

    def run(self):

        gps = Gps.init_gps(self.config['device']['serial'])

        if self.config['device'].getboolean('track_mode'):
            # create directory to store csv
            try:
                os.mkdir("csv/")
            except FileExistsError:
                print('csv/ directory already exist')

            # open file for csv
            todayStr = datetime_module.now().isoformat()
            f = open('csv/'+todayStr+'.csv', 'w')
            writer = csv.writer(f)

        last_message_time = 0
        while True:
            line = str(gps.readline(), "ascii").strip()
            if line:
                try:
                    nmea = pynmea2.parse(line)
                    if nmea.is_valid and nmea.sentence_type == "RMC":
                        datetime = datetime_module.combine(nmea.datestamp, nmea.timestamp)
                        timestamp = datetime_module.timestamp(datetime)
                        
                        if self.config['device'].getboolean('track_mode'):
                            # write to csv for track
                            writer.writerow([timestamp, nmea.latitude, nmea.longitude, nmea.spd_over_grnd * 1.852])
                            f.flush()
                        
                        now = time.monotonic()
                        if now - last_message_time >= 10:
                            msg = message.Message(self.config['device']['id'], line)
                            self.queue.put(msg.to_json())
                            last_message_time = now
                        
                except pynmea2.ParseError as e:
                    print("Error parsing line !", e)
                except AttributeError:
                    continue
                except Exception as e:
                    print("Error writing to csv !", e)

    @staticmethod
    def send_command(gps: adafruit_gps.GPS, command: str):
        gps.send_command(command)
        time.sleep(1)

    @staticmethod
    def init_gps(path: str) -> adafruit_gps.GPS:
        debug = True

        # open serial GPS
        uart = serial.Serial(path, baudrate=9600, timeout=10)
        gps = adafruit_gps.GPS(uart, debug=debug)

        # set baudrate to 115200
        Gps.send_command(gps, b'PMTK251,115200')

        # re-open serial GPS
        uart = serial.Serial(path, baudrate=115200, timeout=10)
        gps = adafruit_gps.GPS(uart, debug=debug)

        # enable only $GPRMC
        Gps.send_command(gps, b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        # set update rate to 10 times per seconds
        Gps.send_command(gps, b'PMTK220,100')
        #Gps.send_command(gps, bytes('PMTK220,{}'.format(100), "ascii"))

        return gps
