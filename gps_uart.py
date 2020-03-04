from datetime import datetime, timedelta
from threading import Thread

import adafruit_gps
import board
import busio
from persistqueue import FIFOSQLiteQueue


class Gps(Thread):

    def __init__(self, path: str, queue: FIFOSQLiteQueue, interval: int):
        Thread.__init__(self)
        self.path = path
        self.queue = queue
        self.interval = interval
        self.lastMessageTime = datetime.now() - timedelta(milliseconds=interval)

    def run(self):
        uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
        gps = adafruit_gps.GPS(uart, debug=False)
        gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        gps.send_command(b'PMTK220,1000')
        while True:
            nmea = gps.nmea_sentence()
            print(nmea)
            self.queue.put(nmea)
