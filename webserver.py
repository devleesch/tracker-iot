import cherrypy;

class WebServer(object):
    @cherrypy.expose
    def index(self):
        try:
            f = open('csv/track.csv', 'r')
        except Exception as e:
            print(e)

        return "Hello world"