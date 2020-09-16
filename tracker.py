import iotcore
import sender
import gps
import cherrypy
import webserver
import configparser
import time
import database

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    database.Database.init()

    conn = database.Database.connect()
    track = database.Track()
    database.TrackServive.insert(conn, track)
    conn.close()

    client = iotcore.IotCore(config)

    t_gps = gps.Gps(config, track)
    t_sender = sender.Sender(config, client)

    t_gps.start()
    t_sender.start()

    cherrypy.server._socket_host = '0.0.0.0'
    cherrypy.quickstart(webserver.WebServer())

if __name__ == "__main__":
    main()
