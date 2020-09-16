import cherrypy;

class WebServer(object):
    @cherrypy.expose
    def index(self):
        return "Hello world"