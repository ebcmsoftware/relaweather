import webapp2
import json
import logging

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
        try: #what gorgeous error checking (not)
            if not (lat and lng) and not zipcode:
                raise TypeError
            if zipcode:
                zipcode = int(zipcode)

                #if they give like "2155" rather than "02155"
                if zipcode < 10000 and self.request.get('zip', None)[0] != '0':
                    raise TypeError
                if zipcode > 99999 or zipcode < 1000:
                    raise TypeError
            if lat:
                lat = float(lat)
                if lat < -90 or lat > 90:
                    raise TypeError
            if lng:
                lng = float(lng)
                if lng < -180 or lng > 180:
                    raise TypeError
        except TypeError:
            logging.warn('Invalid API request - given zip: %s, lat: %s, lng: %s' %(zipcode,lat,lng))
            response['err'] = 'Invalid API request - bad zipcode or lat+lng'
            response['fault'] = 'yours'
            write(response)
            return
        ####/Error checking####

        response['zip'] = zipcode
        response['lat'] = lat
        response['lng'] = lng
        write(response)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('404 lol')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/api', API)
], debug=True)
