from diskcache.persistent import Deque, Index
import webserver
import gps
import logging
import cherrypy
import os
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

    cherrypy.config.update({
        'log.screen': False,
        'log.access_file': '',
        'log.error_file': ''
    })
    cherrypy.server.socket_host = '0.0.0.0'

    cherrypy.tree.mount(webserver.Root(), '/', {
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.getcwd() + '/webapp/dist/webapp',
            'tools.staticdir.index': 'index.html'
        }
    })
    cherrypy.tree.mount(webserver.ConfigApi(), '/api/config')
    cherrypy.tree.mount(webserver.PositionApi(deque, index), '/api/position')
    cherrypy.tree.mount(webserver.ProcessApi(p_gps, p_sender, deque, index), '/api/process')

    cherrypy.engine.start()
    cherrypy.engine.block()