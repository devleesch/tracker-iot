from multiprocessing.context import Process
from threading import Thread
from diskcache import Deque
import time
import uuid
import unittest

import adafruit_gps
import serial
import pynmea2

import config
import model
import logging


logger = logging.getLogger(__name__)
class Gps(Process):

    SLEEP_TIME = 0.05

    def __init__(self):
        Process.__init__(self, daemon=True)
        self.deque = Deque(directory="nmea")
        self.gps = None
        self.stop = False
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
            time.sleep(Gps.SLEEP_TIME)
        
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

    def init(self, rate):
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
        self.init(1000 // frequence)

        while not self.stop:
            logger.info("GpsTrack.run() start session")
            self.wait_for_valid_position()
            self.wait_for_minimum_speed()

            average_speed = SlidingAverage(60 * frequence)
            track = str(uuid.uuid4())
            while not self.stop and (average_speed.value() is None or average_speed.value() > config.parser.getint('track', 'average_speed_threshold')):
                try:
                    line = self.read_nmea()
                    nmea = Gps.parse_nmea(line)
                    if nmea.is_valid:
                        average_speed.append(Gps.to_kmh(nmea.spd_over_grnd))
                        self.last_nmea = line
                        self.deque.append(model.Message(str(uuid.uuid4()), line, track))
                except Exception as e:
                    logger.error(f"GpsTrack.run() : {e}")
                    pass
                time.sleep(Gps.SLEEP_TIME)

            logger.info("GpsTrack.run() session ended")
        logger.info("GpsTrack.run() ended")

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
            time.sleep(Gps.SLEEP_TIME)


class GpsRoad(Gps):
    def run(self):
        logger.info("GpsRoad.run() starting...")
        self.init(1000)

        self.wait_for_valid_position()

        last_timestamp = -config.parser.getfloat('device', 'interval')
        trip = str(uuid.uuid4())
        while not self.stop:
            try:
                line = self.read_nmea()
                self.last_nmea = line
                timestamp = time.monotonic()
                if timestamp - last_timestamp >= config.parser.getfloat('device', 'interval'):
                    nmea = Gps.parse_nmea(line)
                    if nmea.is_valid:
                        self.deque.append(model.Message(str(uuid.uuid4()), line, trip))
                        last_timestamp = timestamp
            except Exception as e:
                logger.error(f"GpsRoad.run() : {e}")
                pass
            time.sleep(Gps.SLEEP_TIME)
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