import logging

import cherrypy

import database
import gps
import iotcore
import sender
import webserver
import config


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
class Tracker:

    def __init__(self) -> None:
        self.t_sender = None
        self.t_gps = None

    def main(self):
        database.Database.init()

        self.start_gps()

        cherrypy.log.screen = False # disable CherryPy stdout logging
        cherrypy.server._socket_host = '0.0.0.0'
        cherrypy.server.socket_port = 80
        cherrypy.quickstart(webserver.WebServer(self))

    def start_sender(self):
        self.t_sender = sender.Sender(iotcore.IotCore())
        self.t_sender.start()

    def stop_sender(self):
        self.t_sender.stop = True

    def start_gps(self):
        if config.parser.getboolean('device', 'track_mode'):
            self.t_gps = gps.GpsTrack(self)
        else:
            self.t_gps = gps.GpsRoad(self)
        self.t_gps.start()

    def stop_gps(self):
        self.t_gps.stop = True


if __name__ == "__main__":
    tracker = Tracker()
    tracker.main()