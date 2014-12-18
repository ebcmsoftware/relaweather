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

        #TODO: VERIFY THIS VERIFY THIS VERIFY THIS PLEEEAAASSSEEEE**************************************************** XXX
        # tri-hourly times are 
            # 0: 2am-5am
            # 1: 5am-8am
            # 2: 8am-11am
            # 3: 11am-2pm
            # 4: 2pm-5pm
            # 5: 5pm-8pm
            # 6: 8pm-11pm
            # 7: 11pm-2am

        def get_avg(data, param, night=False):
            avg = 0.0
            if night:
                for i in range(4): #4*3 = 12. things are measured in 3hr periods, 12hrs is half the day.
                    avg += float(data['data']['weather'][0]['hourly'][(i+5) % 8][param]) # 5, 6, 7, 0
                avg /= 4.0
                return avg
            else:
                for i in range(4): #4*3 = 12. things are measured in 3hr periods, 12hrs is half the day.
                    avg += float(data['data']['weather'][0]['hourly'][i+1][param]) # 1, 2, 3, 4
                avg /= 4.0
                return avg
            pass

        #TODO: find if rain or snow. somehow. be smart
        def get_tomorrow_precip(tomorrow):
            tomorrow_precip = get_avg(tomorrow, 'precipMM') * 4.0
            return tomorrow_precip

        def get_tomorrow_night_precip(tomorrow):
            tomorrow_night_precip = get_avg(tomorrow, 'precipMM', night=True) * 4.0
            return tomorrow_night_precip

        def get_tomorrow_night_temp(today, tomorrow):
            today_min = today['data']['weather'][0]['mintempF']
            tomorrow_min = tomorrow['data']['weather'][0]['mintempF']
            return '(today_min - tomorrow_min): %f' %(float(today_min) - float(tomorrow_min))

        def get_tomorrow_temp(today, tomorrow):
            # daytime
            today_max = today['data']['weather'][0]['maxtempF']
            tomorrow_max = tomorrow['data']['weather'][0]['maxtempF']
            return '(today_max - tomorrow_max): %f' %(float(today_max) - float(tomorrow_max))


        #TODO: find if rain or snow. somehow. be smart
        def get_today_precip(today):
            today_precip = get_avg(today, 'precipMM') * 4.0
            return today_precip

        def get_tonight_precip(today):
            today_precip = get_avg(today, 'precipMM', night=True) * 4.0
            return today_precip

        def get_tonight_temp(yesterday, today):
            today_min = today['data']['weather'][0]['mintempF']
            yesterday_min = yesterday['data']['weather'][0]['mintempF']
            return '(today_min - yesterday_min): %f' %(float(today_min) - float(yesterday_min))

        def get_today_temp(yesterday, today):
            today_max = today['data']['weather'][0]['maxtempF']
            yesterday_max = yesterday['data']['weather'][0]['maxtempF']
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
        #use lat+lng to get data
        #TODAY
        url = 'http://api.openweathermap.org/data/2.5/weather?lat='+lat+'&lon='+lng
        today = json.loads(urllib2.urlopen(url).read())

        if include_today:
            #YESTERDAY - yesterday, midnight (AM)
            url = 'http://api.worldweatheronline.com/free/v2/past-weather.ashx?key='+key+'&format=json&q='+lat+','+lng+'&date='+yesterday_datetime.strftime('%Y-%m-%d')
            yesterday = json.loads(urllib2.urlopen(url).read())
            response['today'] = get_today_temp(yesterday, today)
            response['tonight'] = get_tonight_temp(yesterday, today)
            response['today_precip'] = get_today_precip(today)
            response['tonight_precip'] = get_tonight_precip(today)

        if include_tomorrow:
            #TOMORROW
            url = 'http://api.worldweatheronline.com/free/v2/weather.ashx?key='+key+'&format=json&q='+lat+','+lng+'&date='+tomorrow_datetime.strftime('%Y-%m-%d')
            tomorrow = json.loads(urllib2.urlopen(url).read())
            response['tomorrow'] = get_tomorrow_temp(today, tomorrow)
            response['tomorrow_night'] = get_tomorrow_night_temp(today, tomorrow)
            response['tomorrow_precip'] = get_tomorrow_precip(tomorrow)
            response['tomorrow_night_precip'] = get_tomorrow_night_precip(tomorrow)

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

        ######################### TESTING #######################
        self.response.write('TODAYS DATA:<br>') 
        write(today)
        self.response.write('<br><br>YESTERDAYS DATA:<br>')
        write(yesterday)
        self.response.write('<br><br>TOMORROWS DATA:<br>')
        write(tomorrow)
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

