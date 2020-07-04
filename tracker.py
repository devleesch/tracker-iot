import persistqueue
import signal

import iotcore
import sender
import gps
import cherrypy
import webserver
import configparser
import time

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    client = iotcore.IotCore(config)
    queue = persistqueue.FIFOSQLiteQueue('./queue.sqlite', multithreading=True)

    t_gps = gps.Gps(config, queue)
    t_sender = sender.Sender(queue, client)

    t_gps.start()
    t_sender.start()

    cherrypy.server._socket_host = '0.0.0.0'
    cherrypy.quickstart(webserver.WebServer())

if __name__ == "__main__":
    main()
