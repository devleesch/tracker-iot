import cherrypy;

class WebServer(object):
    @cherrypy.expose
    def index(self):
        f = open('csv/track.csv', 'r')
        return "Hello world"