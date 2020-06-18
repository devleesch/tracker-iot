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
import os
import pynmea2


class Gps(Thread):

    def __init__(self, path, device_id: str, queue: FIFOSQLiteQueue, interval: int):
        Thread.__init__(self)
        self.path = path
        self.device_id = device_id
        self.queue = queue
        self.interval = interval
        self.lastMessageTime = datetime.now() - timedelta(milliseconds=interval)

    def run(self):

        gps = Gps.init_gps(self.path)

        # create directory to store csv
        try:
            os.mkdir("csv/")
        except FileExistsError:
            print('csv/ directory already exist')

        # open file for csv
        todayStr = datetime.now().isoformat()
        f = open('csv/'+todayStr+'.csv', 'w')
        writer = csv.writer(f)

        while True:
            line = gps.readline()
            if line :
                print('line:', line)
                msg = pynmea2.parse(str(line, "ascii").strip())
                # write to csv for track
                try:
                    writer.writerow([datetime.timestamp(msg.timestamp), msg.latitude, msg.longitude, msg.data['spd_over_grnd']])
                    f.flush()
                except:
                    print("Error writing to csv !")

                # nmea = gps.nmea_sentence
                # if nmea is not None:
                #     if nmea.split(",")[0] in tracker.gps_to_send:
                #         now = datetime.now()
                #         if now - self.lastMessageTime > timedelta(milliseconds=self.interval):
                #             timestamp = datetime(
                #                 gps.datetime.tm_year,
                #                 gps.datetime.tm_mon,
                #                 gps.datetime.tm_mday,
                #                 gps.datetime.tm_hour,
                #                 gps.datetime.tm_min,
                #                 gps.datetime.tm_sec
                #             )
                #             msg = message.Message(self.device_id, nmea, timestamp)
                #             print("queueing {}".format(msg.to_json()))
                #             self.queue.put(msg.to_json())
                #             self.lastMessageTime = now

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

        # enable only $GPRMC and $GPGGA
        Gps.send_command(gps, b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        # set update rate to 10 times per seconds
        Gps.send_command(gps, b'PMTK220,100')
        #Gps.send_command(gps, bytes('PMTK220,{}'.format(100), "ascii"))

        return gps
