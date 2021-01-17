from datetime import datetime as datetime_module
from threading import Thread
import os
import time
import uuid

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
        while not line and not line.startswith("$GPRMC"):
            try:
                line = str(self.gps.readline(), "ascii").strip()
            except Exception as e:
                logger.error(f"Gps.read_nmea() : {e}")
        return line

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

    @staticmethod
    def to_kmh(knot):
        return knot * 1.852 if knot else 0

class GpsTrack(Gps):
    def run(self):
        logger.info("GpsTrack.run() starting...")
        self.database_connection = database.Database.connect()
        self.init_gps()
        self.wait_for_valid_position()
        self.wait_for_minimum_speed()

        f = self.create_track_file()

        last_timestamp = time.monotonic()
        while not self.stop:
            try:
                line = self.read_nmea()
                self.last_nmea = line
                f.write(f"{line}\n")
                f.flush()
            except Exception as e:
                logger.error(f"GpsTrack.run() : {e}")
                pass
        logger.info("GpsTrack.run() ended !")

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
            while not todayStr and not self.stop:
                try:
                    nmea = Gps.parse_nmea(self.read_nmea())
                    datetime = datetime_module.combine(nmea.datestamp, nmea.timestamp)
                    todayStr = datetime.isoformat()
                    f = open(f"csv/{todayStr}.csv", 'w')
                except:
                    continue
            logger.info(f"csv/{todayStr}'.csv created !")
        return f

    def wait_for_minimum_speed(self):
        logger.info("waiting for minimum speed...")
        start_move = None
        while not self.stop:
            try:
                line = self.read_nmea()
                nmea = self.parse_nmea(line)
                if nmea and Gps.to_kmh(nmea.spd_over_grnd) >= config.parser.getint('track', 'speed_threshold'):
                    if start_move is None:
                        start_move = time.monotonic()
                else:
                    start_move = None

                if start_move is not None and time.monotonic() - start_move >= 5:
                    logger.info("start moving !")
                    break
            except Exception as e:
                logger.error(f"GpsTrack.wait_for_minimum_speed() : {e}")


class GpsRoad(Gps):
    def run(self):
        logger.info("GpsRoad.run() starting...")
        self.database_connection = database.Database.connect()
        self.init_gps()
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
                time.sleep(1)
            except Exception as e:
                logger.error(f"GpsRoad.run() : {e}")
                pass
        self.tracker.stop_sender()
        logger.info("GpsRoad.run() ended !")
