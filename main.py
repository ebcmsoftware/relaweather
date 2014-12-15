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
            url = 'http://api.openweathermap.org/data/2.5/weather?lat='+lat+'&lon='+lng
            today = json.loads(urllib2.urlopen(url).read())

            #YESTERDAY
            url = 'http://api.openweathermap.org/data/2.5/find?lat='+lat+'&lon='+lng+'&cnt=1'
            yesterday_id = json.loads(urllib2.urlopen(url).read())['list'][0]['id']
            yesterdays_date = datetime.datetime.utcnow() - datetime.timedelta(days=2)
            yesterday_unix = int((yesterdays_date - datetime.datetime(1970,1,1)).total_seconds())
            url = 'http://api.openweathermap.org/data/2.5/history/city?id='+str(yesterday_id)+'&type=daily&start='+str(yesterday_unix)+'&cnt=1'
            yesterday = json.loads(urllib2.urlopen(url).read())

            #TOMORROW
            url = 'http://api.openweathermap.org/data/2.5/forecast/daily?lat='+lat+'&lon='+lng+'&cnt=1&mode=json'
            tomorrow = json.loads(urllib2.urlopen(url).read())
            logging.warn(today)
            logging.warn(tomorrow)
        elif zipcode:
            pass

        d8a = '' + \
        ('TODAYS DATA:<br>') + \
        (json.dumps(today, separators=(',',':'), sort_keys=True)) + \
        ('<br><br>YESTERDAYS DATA:<br>') + \
        (json.dumps(yesterday, separators=(',',':'), sort_keys=True)) + \
        ('<br><br>TOMORROWS DATA:<br>') + \
        (json.dumps(tomorrow, separators=(',',':'), sort_keys=True))
        self.response.write(d8a)
        #write(response)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        template_values = {}
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/api', API),
    ('/', MainHandler)
], debug=True)
