import webserver
import gps
import logging
import cherrypy
from sender import Sender
from diskcache import Deque
import config


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)
class Tracker:
    def main(self):
        deque = Deque(directory="nmea")

        t_sender = Sender(deque)
        t_sender.start()

        if config.parser.getboolean('device', 'track_mode'):
            t_gps = gps.GpsTrack(deque)
        else:
            t_gps = gps.GpsRoad(deque)
        #t_gps.start()

        cherrypy.tree.mount(webserver.Root(), '/', {
            '/': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': '/Users/xavier/dev/tracker/tracker-iot/webapp/dist/webapp',
                'tools.staticdir.index': 'index.html'
            }
        })
        cherrypy.tree.mount(webserver.Api(t_gps, t_sender), '/api')
        cherrypy.engine.start()
        cherrypy.engine.block()


if __name__ == "__main__":
    tracker = Tracker()
    tracker.main()