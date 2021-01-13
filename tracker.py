import configparser
import time

import cherrypy
import database
import gps
import iotcore
import sender
import webserver

config = configparser.ConfigParser()
config.read('config.ini')

class Tracker:
    def __init__(self) -> None:
        self.t_sender = None
        self.t_gps = None

    def main(self):
        database.Database.init()

        self.t_sender = sender.Sender(iotcore.IotCore())
        self.t_sender.start()

        self.start_gps()

        cherrypy.server._socket_host = '0.0.0.0'
        cherrypy.quickstart(webserver.WebServer())

    def start_gps(self):
        if config.getboolean('device', 'track_mode'):
            self.t_gps = gps.GpsTrack()
        else:
            self.t_gps = gps.GpsRoad()
        self.t_gps.start()

    def stop_gps(self):
        self.t_gps.stop = True


if __name__ == "__main__":
    tracker = Tracker()
    tracker.main()