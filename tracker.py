from diskcache.persistent import Deque, Index
import webserver
import gps
import logging
import cherrypy
import os
from sender import Sender


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

class Tracker:
    def __init__(self) -> None:
        self.deque = Deque(directory="nmea")
        self.index = Index()
        self.p_sender = None
        self.p_gps = None

    def start_sender(self):
        if self.p_sender is None or not self.p_sender.is_alive():
            self.p_sender = Sender(self.deque)
            self.p_sender.start()

    def stop_sender(self):
        if self.p_sender is not None and self.p_sender.is_alive():
            self.p_sender.terminate()
            self.p_sender.join()
    
    def start_gps(self):
        if self.p_gps is None or not self.p_gps.is_alive():
            self.p_gps = gps.Gps.get(self.deque, self.index)
            self.p_gps.start()

    def stop_gps(self):
        if self.p_gps is not None and self.p_gps.is_alive():
            self.p_gps.terminate()
            self.p_gps.join()


if __name__ == "__main__":

    tracker = Tracker()
    tracker.start_sender()
    tracker.start_gps()

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
    cherrypy.tree.mount(webserver.ConfigApi(tracker), '/api/config')
    cherrypy.tree.mount(webserver.PositionApi(tracker), '/api/position')
    cherrypy.tree.mount(webserver.ProcessApi(tracker), '/api/process')
    cherrypy.tree.mount(webserver.SystemApi(), '/api/system')

    cherrypy.engine.start()
    cherrypy.engine.block()