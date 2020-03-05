from datetime import datetime, timedelta
from threading import Thread

import adafruit_gps
import board
import serial
from persistqueue import FIFOSQLiteQueue
import message


class Gps(Thread):

    def __init__(self, path, device_id: str, queue: FIFOSQLiteQueue, interval: int):
        Thread.__init__(self)
        self.path = path
        self.device_id = device_id
        self.queue = queue
        self.interval = interval
        self.lastMessageTime = datetime.now() - timedelta(milliseconds=interval)

    def run(self):
        uart = serial.Serial(self.path, baudrate=9600, timeout=10)
        gps = adafruit_gps.GPS(uart, debug=False)
        # enable only $GPRMC
        gps.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        gps.send_command(b'PMTK220,1000')
        while True:
            nmea = gps.nmea_sentence
            msg = message.Message(self.device_id, nmea)
            self.queue.put(msg.to_json())
