import cherrypy;
from jinja2 import Environment, PackageLoader, select_autoescape
import os
import model
from operator import attrgetter
import laptime


class WebServer(object):


    def __init__(self):
        self.env = Environment(
            loader=PackageLoader('webserver', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.tracks = model.TRACKS


    @cherrypy.expose
    def index(self):
        files = os.listdir("csv")
        template = self.env.get_template('index.html')
        return template.render(
            files = sorted(files, reverse = True),
            tracks = sorted(self.tracks, key=attrgetter("id"))
        )

    
    @cherrypy.expose
    def laptime(self, file, track_id):
        track = None
        for t in model.TRACKS:
            if t.id == int(track_id):
                track = t
                continue
        laps = laptime.calculate_laptime(file, track)
        
        template = self.env.get_template('laptime.html')
        return template.render(
            laps = laps
        )