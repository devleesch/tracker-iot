from sender import Sender
from gps import Gps
import cherrypy;
import logging
import config


logger = logging.getLogger(__name__)

class Api:
    def __init__(self, t_gps: Gps, t_sender: Sender) -> None:
        self.t_gps = t_gps
        self.t_sender = t_sender

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def last_nmea(self):
        position = Gps.parse_nmea(self.t_gps.last_nmea)
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
        

# static files
class Root:
    pass
