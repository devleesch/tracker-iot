from multiprocessing.context import Process
from threading import Thread
from diskcache.persistent import Deque, Index
from sender import Sender
from gps import Gps
import cherrypy;
import logging
import config


logger = logging.getLogger(__name__)

class Api:
    def __init__(self, p_gps: Gps, p_sender: Sender, deque: Deque, index: Index) -> None:
        self.p_gps = p_gps
        self.p_sender = p_sender
        self.deque = deque
        self.index = index

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def last_nmea(self):
        position = Gps.parse_nmea(self.index["nmea"])
        return {
            'latitude': position.latitude,
            'longitude': position.longitude
        }


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def config(self):
        response = {}
        for key, value in config.parser.items('device'):
            response[key] = value
        return response

    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def start(self, process: str):
        p = self.get_process(process)
        if not p.is_alive():
            if process == "gps":
                self.p_gps = Gps.get(self.deque, self.index)
            elif process == "sender":
                self.p_sender = Sender(self.deque)
            
            p = self.get_process(process)
            p.start()

        return self.process_status()


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def stop(self, process: str):
        p = self.get_process(process)
        if p.is_alive():
            p.terminate()
            p.join()

        return self.process_status()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def process_status(self):
        return {
            'gps': self.p_gps.is_alive(),
            'sender': self.p_sender.is_alive()
        }

    def get_process(self, process: str) -> Process:
        if process == "gps":
            p = self.p_gps
        elif process == "sender":
            p = self.p_sender
        return p
        

# static files
class Root:
    pass
