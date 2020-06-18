from datetime import datetime, timedelta
from threading import Thread
from persistqueue import FIFOSQLiteQueue
import adafruit_gps
import board
import serial
import message
import tracker
import time
import csv


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
        # enable only $GPRMC and $GPGGA
        Gps.send_command(gps, b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        # set update rate to 10 times per seconds
        Gps.send_command(gps, bytes('PMTK220,{}'.format(100), "ascii"))
        # open file for csv
        todayStr = datetime.now().isoformat()
        f = open('csv/'+todayStr+'.csv', 'w')
        writer = csv.writer(f)
        while True:
            gps.update()
            writer.writerow([gps.timestamp_utc, gps.latitude, gps.longitude, gps.speed_knots])
            nmea = gps.nmea_sentence
            if nmea is not None:
                if nmea.split(",")[0] in tracker.gps_to_send:
                    now = datetime.now()
                    if now - self.lastMessageTime > timedelta(milliseconds=self.interval):
                        timestamp = datetime(
                            gps.datetime.tm_year,
                            gps.datetime.tm_mon,
                            gps.datetime.tm_mday,
                            gps.datetime.tm_hour,
                            gps.datetime.tm_min,
                            gps.datetime.tm_sec
                        )
                        msg = message.Message(self.device_id, nmea, timestamp)
                        print("queueing {}".format(msg.to_json()))
                        self.queue.put(msg.to_json())
                        self.lastMessageTime = now
            time.sleep(0.05)

    @staticmethod
    def send_command(gps: adafruit_gps.GPS, command: str):
        gps.send_command(command)
        time.sleep(1)
