from multiprocessing.context import Process
import re
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

    GPS_PROCESS = "GPS"
    SENDER_PROCESS = "SENDER"

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
            if process == ProcessApi.GPS_PROCESS:
                self.p_gps = Gps.get(self.deque, self.index)
            elif process == ProcessApi.SENDER_PROCESS:
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
            'sender': self.p_sender.is_alive(),
        }

    def __get_process(self, process: str) -> Process:
        if process == ProcessApi.GPS_PROCESS:
            p = self.p_gps
        elif process == ProcessApi.SENDER_PROCESS:
            p = self.p_sender
        return p


class ConfigApi:

    def __init__(self, p_gps: Gps, deque: Deque, index: Index) -> None:
        self.p_gps = p_gps
        self.deque = deque
        self._index = index

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        response = {}
        response['id'] = config.parser.get('device', 'id')
        response['track_mode'] = config.parser.getboolean('device', 'track_mode')
        return response

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update(self):
        body = cherrypy.request.json
        config.parser.set('device', 'track_mode', str(body['track_mode']))

        self.p_gps.terminate()
        self.p_gps.join()
        self.p_gps = Gps.get(self.deque, self._index)
        self.p_gps.start()

        return self.index()

# static files
class Root:
    pass
