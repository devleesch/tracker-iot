import cherrypy;
from jinja2 import Environment, PackageLoader, select_autoescape
import os
import model


class WebServer(object):


    def __init__(self):
        self.env = Environment(
            loader=PackageLoader('webserver', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.tracks = [
            model.Track(1, "Mettet", model.Position(latitude=50.300936, longitude=4.649522), model.Position(latitude=50.300821, longitude=4.649592)),
            model.Track(2, "Chambley", model.Position(latitude=0, longitude=0), model.Position(latitude=0, longitude=0))
        ]


    @cherrypy.expose
    def index(self):
        files = os.listdir("csv")
        template = self.env.get_template('index.html')
        return template.render(
            files = sorted(files, reverse = True),
            tracks = sorted(self.tracks, key="id")
        )