import webapp2
import json

class API(webapp2.RequestHandler):
    def options(self):      
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT'

    def get(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT'
        self.response.write('its gonna b colder 2morrow')

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('404 lol')

app = webapp2.WSGIApplication([
    ('/', MainHandler)
    ('/api', API)
], debug=True)
