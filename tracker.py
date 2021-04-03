import gps
from os import system
import time
from iotcore import IotCore
import logging
from sender import Sender
import uuid
import serial
import adafruit_gps
import config
import model
from diskcache import Deque


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)
class Tracker:
    def main(self):
        deque = Deque(directory="nmea")

        t_sender = Sender(deque)
        t_sender.start()

        t_gps = gps.GpsTrack(deque)
        t_gps.start()

        while True:
            time.sleep(1)


if __name__ == "__main__":
    tracker = Tracker()
    tracker.main()