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

        # Writes a dict to the response
        def write(response):
            self.response.write(json.dumps(response, separators=(',',':'), sort_keys=True))

        # temp in Celsius, vapor_pressure in kPa, wind_speed in m/sec
        def feelslike(temp, vapor_pressure, wind_speed):
            return -2.7 + 1.04*(temp-273.15) + 2.0*vapor_pressure - 0.65*wind_speed

        #TODO: LOGIC
        def get_tomorrow(today, tomorrow):
            today_temp = today['main']['temp']
            today_pressure = today['main']['pressure'] / 10.0
            today_speed = today['wind']['speed']

            tomorrow_temp = tomorrow['list'][0]['temp']['day']
            tomorrow_pressure = tomorrow['list'][0]['pressure'] / 10.0
            tomorrow_speed = tomorrow['list'][0]['speed']

            today_feelslike = feelslike(today_temp, today_pressure, today_speed)
            tomorrow_feelslike = feelslike(tomorrow_temp, tomorrow_pressure, tomorrow_speed)

            return [today_pressure, tomorrow_pressure]
            return [today_feelslike, tomorrow_feelslike]

        #TODO: LOGIC
        def get_today(yesterday, today):
            return 'colder'

        # Error checking and input validation
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

        if not lat or not lng:
            url = 'https://maps.googleapis.com/maps/api/geocode/json?address='+zipcode+'&key=AIzaSyCGA86L8v4Lh-AUJHsKvQODP8SNsbTjYqg'
            location = json.loads(urllib2.urlopen(url).read())
            lat = str(location['results'][0]['geometry']['location']['lat'])
            lng = str(location['results'][0]['geometry']['location']['lng'])
        #use lat+lng to get data
        #TODAY
        url = 'http://api.openweathermap.org/data/2.5/weather?lat='+lat+'&lon='+lng
        today = json.loads(urllib2.urlopen(url).read())

        #YESTERDAY
        url = 'http://api.openweathermap.org/data/2.5/station/find?lat='+lat+'&lon='+lng+'&cnt=1' #get a lot of nearby stations? idk
        yesterday_id = today['sys']['id'] # weather station ID of the data gotten from 'todays data'
        url = 'http://api.openweathermap.org/data/2.5/history/station?id='+str(yesterday_id)+'&type=hour&cnt=30'
        url = 'http://api.openweathermap.org/data/2.5/history/station?id='+str(yesterday_id)+'&type=day&type=tick&cnt=20'
        yesterday = json.loads(urllib2.urlopen(url).read())

        #TOMORROW
        url = 'http://api.openweathermap.org/data/2.5/forecast/daily?lat='+lat+'&lon='+lng+'&cnt=1&mode=json'
        tomorrow = json.loads(urllib2.urlopen(url).read())

        #LOCATION
        url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng='+lat+','+lng+'&key=AIzaSyCGA86L8v4Lh-AUJHsKvQODP8SNsbTjYqg'
        location = json.loads(urllib2.urlopen(url).read())

        response['tomorrow'] = get_tomorrow(today, tomorrow)
        response['today'] = get_today(yesterday, today)
        response['city'] = location['results'][0]['address_components'][2]['long_name']
        if location['results'][0]['address_components'][5]['short_name'] != 'US': #THEN THEY ARE A COMMUNIST
            response['state'] = location['results'][0]['address_components'][5]['short_name']
            response['zip'] = '666'
        else:
            response['state'] = location['results'][0]['address_components'][4]['short_name']
            response['zip'] = location['results'][0]['address_components'][6]['short_name']
        write(response)
        return # send the data
        write(yesterday)



class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        template_values = {}
        self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([
    ('/api', API),
    ('/', MainHandler)
], debug=True)

