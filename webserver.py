import cherrypy;
from jinja2 import Environment, PackageLoader, select_autoescape
import config
import tracker


class WebServer(object):

    def __init__(self, tracker: 'tracker.Tracker'):
        self.tracker = tracker
        self.env = Environment(
            loader=PackageLoader('webserver', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )

    @cherrypy.expose
    def index(self, track_mode = config.parser.getboolean('device', 'track_mode')):
        template = self.env.get_template('index.html')

        track_mode = WebServer.getboolean(track_mode)
        if track_mode != config.parser.getboolean('device', 'track_mode'):
            print(f"change track_mode to {track_mode}")
            config.parser['device']['track_mode'] = str(track_mode)
            config.parser.write(open('config.ini', 'w'))
            self.tracker.stop_gps()
            self.tracker.start_gps()

        return template.render(
            track_mode = track_mode
        )

    @staticmethod
    def getboolean(value):
        if isinstance(value, bool):
            return value
        return True if value == 'True' else False
