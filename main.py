import webapp2
import json
import logging
import urllib2

class API(webapp2.RequestHandler):
    def options(self):      
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT'

    def get(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT'

        def write(response):
            self.response.write(json.dumps(response, separators=(',',':')))

        ####Error checking and input validation####
        zipcode = self.request.get('zip', None)
        lat = self.request.get('lat', None)
        lng = self.request.get('lng', None)

        response = {}
        try: # what gorgeous error checking (not)
            if not (lat and lng) and not zipcode:
                raise TypeError
            if zipcode:
                zi = int(zipcode)
                if len(zipcode) != 5:
                    raise TypeError
            if lat:
                latf = float(lat)
                if latf < -90 or latf > 90:
                    raise TypeError
            if lng:
                lngf = float(lng)
                if lngf < -180 or lngf > 180:
                    raise TypeError
        except TypeError:
            logging.warn('Invalid API request - given zip: %s, lat: %s, lng: %s' %(zipcode,lat,lng))
            response['err'] = 'Invalid API request - bad zipcode or lat+lng'
            response['fault'] = 'yours'
            write(response)
            return
        ####/Error checking####

        response['tomorrow'] = 'a bit cooler - rainy'
        url = 'http://api.openweathermap.org/data/2.5/weather?lat='+lat+'&lon='+lng
        today = json.loads(urllib2.urlopen(url).read())
        url = 'http://api.openweathermap.org/data/2.5/forecast/daily?lat='+lat+'&lon='+lng+'&cnt=1&mode=json'
        tomorrow = json.loads(urllib2.urlopen(url).read())
        logging.warn(today)
        logging.warn(tomorrow)

        d8a = '' + \
        ('TODAYS DATA:<br>') + \
        (json.dumps(today, separators=(',',':'))) + \
        ('<br><br>TOMORROWS DATA:<br>') + \
        (json.dumps(tomorrow, separators=(',',':')))
        self.response.write(d8a)
        #write(response)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('404 lol')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/api', API)
], debug=True)
