import configparser

import cherrypy
import database
import gps
import iotcore
import sender
import webserver
import os


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    database.Database.init()

    client = iotcore.IotCore(config)

    t_gps = gps.Gps(config)
    t_gps.start()

    t_sender = sender.Sender(client)
    t_sender.start()

    path = os.path.abspath(os.path.dirname(__file__))
    cherrypy.server._socket_host = '0.0.0.0'
    cherrypy.quickstart(webserver.WebServer())


if __name__ == "__main__":
    main()
