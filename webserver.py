import cherrypy;
from cherrypy.lib import cptools
from jinja2 import Environment, PackageLoader, select_autoescape
import logging

import config
import tracker


logger = logging.getLogger(__name__)
class WebServer(object):

    def __init__(self, tracker: 'tracker.Tracker'):
        self.tracker = tracker
        self.env = Environment(
            loader=PackageLoader('webserver', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )

    @cherrypy.expose
    def index(self, track_mode = None):
        if track_mode:
            track_mode = WebServer.getboolean(track_mode)
            if track_mode != config.parser.getboolean('device', 'track_mode'):
                logger.info(f"change track_mode to {track_mode}")
                config.parser['device']['track_mode'] = str(track_mode)
                config.parser.write(open('config.ini', 'w'))
                self.tracker.stop_gps()
                logger.info("waiting for GPS to shutdown...")
                self.tracker.t_gps.join()
                self.tracker.start_gps()
            cptools.redirect('/')
        else:
            template = self.env.get_template('index.html')
            return template.render(
                track_mode = config.parser.getboolean('device', 'track_mode'),
                last_nmea = self.tracker.t_gps.last_nmea
            )

    @staticmethod
    def getboolean(value):
        if isinstance(value, bool):
            return value
        return True if value == 'True' else False
