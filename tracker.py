import persistqueue

import iotcore
import sender
import gps
import cherrypy
import webserver
import configparser

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    client = iotcore.IotCore(config)
    queue = persistqueue.FIFOSQLiteQueue('./queue.sqlite', multithreading=True)

    g = gps.Gps(config, queue)
    s = sender.Sender(queue, client)

    g.start()
    s.start()

    cherrypy.server._socket_host = '0.0.0.0'
    cherrypy.quickstart(webserver.WebServer())

if __name__ == "__main__":
    main()
