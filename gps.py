from datetime import datetime as datetime_module
from threading import Thread
import os
import time
import uuid
import unittest

import adafruit_gps
from paho.mqtt.client import LOGGING_LEVEL
import serial
import pynmea2

import config
import database
import model
import tracker
import logging


logger = logging.getLogger(__name__)
class Gps(Thread):
    def __init__(self, tracker: 'tracker.Tracker'):
        Thread.__init__(self, name="gps", daemon=True)
        self.database_connection = None
        self.gps = None
        self.stop = False
        self.tracker = tracker
        self.last_nmea = None

    def wait_for_valid_position(self):
        logger.info("waiting GPS fix...")
        while not self.stop:
            nmea = Gps.parse_nmea(self.read_nmea())
            try:
                if nmea and nmea.is_valid:
                    logger.info("GPS fix acquired !")
                    break
            except:
                pass
        
    def read_nmea(self) -> str:
        line = None
        while not line or not line.startswith("$GPRMC"):
            try:
                line = str(self.gps.readline(), "ascii").strip()
            except Exception as e:
                logger.error(f"Gps.read_nmea() : {e}")
        return line

    def send_command(self, command: str):
        self.gps.send_command(command)
        time.sleep(1)

    def init_gps(self, rate):
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
        self.send_command(str.encode(f'PMTK220,{rate}'))

    @staticmethod
    def parse_nmea(line: str):
        if line:
            try:
                return pynmea2.parse(line)
            except pynmea2.ParseError:
                pass
        return None

    @staticmethod
    def to_kmh(knot):
        return knot * 1.852 if knot else 0

class GpsTrack(Gps):
    def run(self):
        frequence = 10
        logger.info("GpsTrack.run() starting...")
        self.init_gps(1000 // frequence)

        while not self.stop:
            logger.info("GpsTrack.run() start session")
            self.wait_for_valid_position()
            self.wait_for_minimum_speed()

            f = self.create_track_file()

            last_flush = time.monotonic()
            average_speed = SlidingAverage(60 * frequence)
            while not self.stop and (average_speed.value() is None or average_speed.value() > config.parser.getint('track', 'average_speed_threshold')):
                try:
                    line = self.read_nmea()
                    nmea = Gps.parse_nmea(line)
                    average_speed.append(Gps.to_kmh(nmea.spd_over_grnd))
                    self.last_nmea = line
                    f.write(f"{line}\n")

                    now = time.monotonic()
                    if now - last_flush >= 5:
                        f.flush()
                        last_flush = now

                except Exception as e:
                    logger.error(f"GpsTrack.run() : {e}")
                    pass
            f.close()
            logger.info("GpsTrack.run() session ended")
        logger.info("GpsTrack.run() ended")

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
            while not self.stop and not todayStr:
                try:
                    nmea = Gps.parse_nmea(self.read_nmea())
                    datetime = datetime_module.combine(nmea.datestamp, nmea.timestamp)
                    todayStr = datetime.isoformat()
                    f = open(f"csv/{todayStr}.csv", 'w')
                except:
                    continue
            logger.info(f"csv/{todayStr}'.csv created")
        return f

    def wait_for_minimum_speed(self):
        logger.info("waiting for minimum speed...")
        average_speed = SlidingAverage(5 * 10)
        while not self.stop and (average_speed.value() is None or average_speed.value() < config.parser.getint('track', 'minimum_speed_threshold')):
            try:
                line = self.read_nmea()
                nmea = self.parse_nmea(line)
                average_speed.append(Gps.to_kmh(nmea.spd_over_grnd))
            except Exception as e:
                logger.error(f"GpsTrack.wait_for_minimum_speed() : {e}")
        


class GpsRoad(Gps):
    def run(self):
        logger.info("GpsRoad.run() starting...")
        self.database_connection = database.Database.connect()
        self.init_gps(1000)
        self.tracker.start_sender()

        self.wait_for_valid_position()

        last_timestamp = -config.parser.getfloat('device', 'interval')
        while not self.stop:
            try:
                line = self.read_nmea()
                self.last_nmea = line
                timestamp = time.monotonic()
                if timestamp - last_timestamp >= config.parser.getfloat('device', 'interval'):
                    database.QueueService.insert(self.database_connection, model.Message(str(uuid.uuid4()), line))
                    last_timestamp = timestamp
            except Exception as e:
                logger.error(f"GpsRoad.run() : {e}")
                pass
        self.tracker.stop_sender()
        logger.info("GpsRoad.run() ended")

class SlidingAverage:
    def __init__(self, size) -> None:
        self.size = size
        self.values = []

    def append(self, value):
        self.values.append(value)
        while len(self.values) > self.size:
            self.values.pop(0)

    def value(self):
        if len(self.values) == 0:
            return None

        if len(self.values) < self.size:
            return None
        
        return sum(self.values) / len(self.values)


class Test(unittest.TestCase):
    def test_sliding_average(self):
        sut = SlidingAverage(5)
        for i in range(10):
            sut.append(10)
        self.assertEquals(10, sut.value())

if __name__ == "__main__":
    unittest.main()