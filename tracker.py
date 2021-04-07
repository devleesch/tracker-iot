from diskcache.persistent import Deque, Index
import webserver
import gps
import logging
import cherrypy
from sender import Sender


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

if __name__ == "__main__":

    deque = Deque(directory="nmea")
    index = Index()

    p_sender = Sender(deque)
    p_sender.start()

    p_gps = gps.Gps.get(deque, index)
    p_gps.start()

    cherrypy.tree.mount(webserver.Root(), '/', {
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '/Users/xavier/dev/tracker/tracker-iot/webapp/dist/webapp',
            'tools.staticdir.index': 'index.html'
        }
    })
    cherrypy.tree.mount(webserver.Api(p_gps, p_sender, deque, index), '/api')
    cherrypy.engine.start()
    cherrypy.engine.block()