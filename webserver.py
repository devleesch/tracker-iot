from multiprocessing.context import Process
from threading import Thread
from diskcache.persistent import Deque, Index
from sender import Sender
from gps import Gps
import cherrypy;
import logging
import config


logger = logging.getLogger(__name__)

class PositionApi:
    def __init__(self, deque: Deque, index: Index) -> None:
        self.deque = deque
        self.index = index

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def last(self):
        raw = self.index["nmea"]
        position = Gps.parse_nmea(raw)
        return {
            'raw': raw,
            'latitude': position.latitude,
            'longitude': position.longitude
        }

        
class ProcessApi:
    def __init__(self, p_gps: Gps, p_sender: Sender, deque: Deque, index: Index) -> None:
        self.p_gps = p_gps
        self.p_sender = p_sender
        self.deque = deque
        self.index = index

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def start(self):
        body = cherrypy.request.json
        process = body["process"]
        p = self.__get_process(process)
        if not p.is_alive():
            if process == "gps":
                self.p_gps = Gps.get(self.deque, self.index)
            elif process == "sender":
                self.p_sender = Sender(self.deque)
            
            p = self.__get_process(process)
            p.start()

        return self.status()


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def stop(self):
        body = cherrypy.request.json
        process = body["process"]
        p = self.__get_process(process)
        if p.is_alive():
            p.terminate()
            p.join()

        return self.status()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def status(self):
        return {
            'gps': self.p_gps.is_alive(),
            'sender': self.p_sender.is_alive()
        }

    def __get_process(self, process: str) -> Process:
        if process == "gps":
            p = self.p_gps
        elif process == "sender":
            p = self.p_sender
        return p


class ConfigApi:
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        response = {}
        for key, value in config.parser.items('device'):
            response[key] = value
        return response


# static files
class Root:
    pass
