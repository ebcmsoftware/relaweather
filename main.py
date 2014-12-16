import webapp2
import datetime
import os
import jinja2
import json
import logging
import urllib2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

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
            self.response.write(json.dumps(response, separators=(',',':'), sort_keys=True))

        #TODO: LOGIC
        def get_tomorrow(today, tomorrow):
            return 'hotter'

        #TODO: LOGIC
        def get_today(yesterday, today):
            return 'colder'

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

        if lat and lng:
            #TODAY
            url = 'http://api.openweathermap.org/data/2.5/weather?lat='+lat+'&lon='+lng
            today = json.loads(urllib2.urlopen(url).read())

            #YESTERDAY
            url = 'http://api.openweathermap.org/data/2.5/station/find?lat='+lat+'&lon='+lng+'&cnt=1' #get a lot of nearby stations? idk
            yesterday_id = json.loads(urllib2.urlopen(url).read())[0]['station']['id'] # station ID of the closest station to that user
            url = 'http://api.openweathermap.org/data/2.5/history/station?id='+str(yesterday_id)+'&type=hour&cnt=30'
            yesterday = json.loads(urllib2.urlopen(url).read())

            #TOMORROW
            url = 'http://api.openweathermap.org/data/2.5/forecast/daily?lat='+lat+'&lon='+lng+'&cnt=1&mode=json'
            tomorrow = json.loads(urllib2.urlopen(url).read())
        elif zipcode:
            pass

        response['tomorrow'] = get_tomorrow(today, tomorrow)
        response['today'] = get_today(yesterday, today)
        write(response)
        return

        ######################### TESTING #######################
        d8a = '' + \
        ('TODAYS DATA:<br>') + \
        (json.dumps(today, separators=(',',':'), sort_keys=True)) + \
        ('<br><br>YESTERDAYS DATA:<br>') + \
        (json.dumps(yesterday, separators=(',',':'), sort_keys=True)) + \
        ('<br><br>TOMORROWS DATA:<br>') + \
        (json.dumps(tomorrow, separators=(',',':'), sort_keys=True))
        self.response.write(d8a)
        ######################### /TESTING ######################


class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        template_values = {}
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/api', API),
    ('/', MainHandler)
], debug=True)
