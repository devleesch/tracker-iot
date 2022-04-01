from multiprocessing.context import Process
import re
from threading import Thread
from tracker import Tracker
from diskcache.persistent import Deque, Index
from sender import Sender
from gps import Gps
import cherrypy;
import logging
import config
import os


logger = logging.getLogger(__name__)

class PositionApi:
    def __init__(self, tracker: Tracker) -> None:
        self.tracker = tracker

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def last(self):
        raw = self.tracker.index["nmea"]
        position = Gps.parse_nmea(raw)
        return {
            'raw': raw,
            'latitude': position.latitude,
            'longitude': position.longitude
        }

        
class ProcessApi:

    GPS_PROCESS = "GPS"
    SENDER_PROCESS = "SENDER"

    def __init__(self, tracker: Tracker) -> None:
        self.tracker = tracker

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def start(self):
        body = cherrypy.request.json
        process = body["process"]
        if process == ProcessApi.GPS_PROCESS:
            self.tracker.start_gps()
        elif process == ProcessApi.SENDER_PROCESS:
            self.tracker.start_sender()

        return self.status()


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def stop(self):
        body = cherrypy.request.json
        process = body["process"]
        if process == ProcessApi.GPS_PROCESS:
            self.tracker.stop_gps()
        elif process == ProcessApi.SENDER_PROCESS:
            self.tracker.stop_sender()

        return self.status()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def status(self):
        return {
            'gps': self.tracker.p_gps.is_alive(),
            'sender': self.tracker.p_sender.is_alive(),
        }


class ConfigApi:

    def __init__(self, tracker: Tracker) -> None:
        self.tracker = tracker

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

        self.tracker.stop_gps()
        self.tracker.start_gps()

        return self.index()

class SystemApi:

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def poweroff(self):
        response = {}
        response['returned_value'] = os.system("poweroff")
        return response

# static files
class Root:
    pass
