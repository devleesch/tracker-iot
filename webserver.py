import cherrypy;
from jinja2 import Environment, PackageLoader, select_autoescape
import os


class WebServer(object):

    def __init__(self):
        self.env = Environment(
            loader=PackageLoader('webserver', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )

    @cherrypy.expose
    def index(self):
        files = os.listdir("csv")
        template = self.env.get_template('index.html')
        return template.render(
            files = sorted(files, reverse = True)
        )