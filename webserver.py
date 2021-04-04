from sender import Sender
from gps import Gps
import cherrypy;
import logging


logger = logging.getLogger(__name__)

class Api:
    def __init__(self, t_gps: Gps, t_sender: Sender) -> None:
        self.t_gps = t_gps
        self.t_sender = t_sender

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def last_nmea(self):
        return {"last_nmea": self.t_gps.last_nmea}

# static files
class Root:
    pass
