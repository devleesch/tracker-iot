import configparser

import cherrypy
import database
import gps
import iotcore
import sender
import webserver


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    database.Database.init()

    client = iotcore.IotCore(config)

    t_gps = gps.Gps(config)
    t_sender = sender.Sender(config, client)

    t_gps.start()
    t_sender.start()

    cherrypy.server._socket_host = '0.0.0.0'
    cherrypy.quickstart(webserver.WebServer())

if __name__ == "__main__":
    main()
