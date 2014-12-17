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

        #TODO: LOGIC
        # tri-hourly times are 
            # 0: 12am
            # 1: 3am
            # 2: 6am
            # 3: 9am
            # 4: 12pm
            # 5: 3pm
            # 6: 6pm
            # 7: 9pm
        # lol im not sure on this just a guess.
        def get_tomorrow(today, tomorrow):
            # daytime
            today_max = today['data']['weather'][0]['maxtempF']
            tomorrow_max = tomorrow['data']['weather'][0]['maxtempF']

            #TODO: nighttime

            return '(today_max - tomorrow_max): %f' %(float(today_max) - float(tomorrow_max))

        def get_today(yesterday, today):
            # daytime
            today_max = today['data']['weather'][0]['maxtempF']
            yesterday_max = yesterday['data']['weather'][0]['maxtempF']

            #TODO: nighttime

            return '(today_max - yesterday_max): %f' %(float(today_max) - float(yesterday_max))

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

        key = '71f6bcee6c068c552bf84460d5409'
        yesterday_datetime = datetime.date.today() - datetime.timedelta(1)
        tomorrow_datetime = datetime.date.today() + datetime.timedelta(1)
        #TODAY
        url = 'http://api.worldweatheronline.com/free/v2/past-weather.ashx?key='+key+'&format=json&q='+lat+','+lng
        today = json.loads(urllib2.urlopen(url).read())

        #YESTERDAY - yesterday, midnight (AM)
        url = 'http://api.worldweatheronline.com/free/v2/past-weather.ashx?key='+key+'&format=json&q='+lat+','+lng+'&date='+yesterday_datetime.strftime('%Y-%m-%d')
        yesterday = json.loads(urllib2.urlopen(url).read())

        #TOMORROW
        url = 'http://api.worldweatheronline.com/free/v2/weather.ashx?key='+key+'&format=json&q='+lat+','+lng+'&date='+tomorrow_datetime.strftime('%Y-%m-%d')
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

