#big thx to worldweatheronline api

import os
import json
import time
import jinja2
import random
import logging
import urllib2
import webapp2
import datetime


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


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

# hourly average for param
def avg(weather_data, param, night=False):
    avg = 0.0
    if night:
        for i in range(4): #4*3 = 12. things are measured in 3hr periods, 12hrs is half the day.
            avg += float(weather_data['data']['weather'][0]['hourly'][(i+5) % 8][param]) # 5, 6, 7, 0
        avg /= 12.0
        return avg
    else:
        for i in range(4): #4*3 = 12. things are measured in 3hr periods, 12hrs is half the day.
            avg += float(weather_data['data']['weather'][0]['hourly'][i+1][param]) # 1, 2, 3, 4
        avg /= 12.0
        return avg

#generalized precip getter
#TODO: find if rain or snow. somehow. be smart. use ['weatherDesc']['value']?
#TODO: thresholldddssssssss
def precip_forecast(total_precip):
    # (hourly avg over 12 hrs) * 12 = total
    # total precipitation (in MM? doesnt seem right.) for today
    if total_precip == 0:
        return None
    if total_precip < 1:
        return random.choice(['occasionally drizzly', 'sprikles'])
    elif total_precip < 5.0:
        return random.choice(['with a little precipitation', 'with slight rain', 'with some showers'])
    elif total_precip < 20.0: 
        return 'rainy'
    else:
        return 'v. rainy'

def temp_forecast(temp_before, temp_after):
    today_diff = float(temp_after) - float(temp_before)
    hot_or_cold = ''
    if today_diff == 0:
        return 'about the same temperature'
    if today_diff > 0:
        hot_or_cold = 'hotter'
    else:
        hot_or_cold = 'colder'
    today_diff = abs(today_diff)
    # begin CSC
    if today_diff < 3:
        adj = random.choice(['a little', 'a bit', 'slightly'])
    elif today_diff < 6:
        adj = random.choice(['', 'noticeably'])
        if adj == '':
            return hot_or_cold
    else:
        adj = random.choice(['a fuck ton'])
    return adj + ' ' + hot_or_cold

def today_forecast(yesterday, today):
    today_max = today['data']['weather'][0]['maxtempF']
    yesterday_max = yesterday['data']['weather'][0]['maxtempF']

    temperature = temp_forecast(yesterday_max, today_max)
    precip = precip_forecast(today)
    # CSC
    if precip != None:
        to_return = 'today will be ' + temperature + ' and ' + precip + ' than yesterday'
        logging.info(to_return)
        return to_return
    else:
        to_return = 'today will be ' + temperature + ' than yesterday'
        logging.info(to_return)
        return to_return

def tomorrow_forecast(today, tomorrow):
    temperature = get_temp_forecast(yesterday, today)
    precip = precip_forecast(tomorrow)
    # CSC
    if precip != None:
        logging.info(temperature + ' and ' + precip)
        return temperature + ' and ' + precip
    else:
        logging.info(temperature)
        return temperature

def search_location(location, address_component, param='short_name'):
    components = location['results'][0]['address_components']
    for component in components:
        if address_component in component['types']:
            return component[param]

class API(webapp2.RequestHandler):
    def options(self):      
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT'

    def get(self, req_type=None):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT'

        # Writes a dict to the response
        def write(response):
            self.response.write(json.dumps(response, separators=(',',':'), sort_keys=True))

# Error checking and input validation
        response = {}

        include_today = True
        include_tomorrow = True
        if req_type:
            include_today = (req_type == 'today')
            include_tomorrow = (req_type == 'tomorrow')

        if not include_today and not include_tomorrow:
            logging.warn('Invalid API request - given req_type: "' + req_type + '"')
            response['err'] = 'Invalid API request - bad API request type "' + req_type + '"'
            response['fault'] = 'yours'
            write(response)
            return

        zipcode = self.request.get('zip', None)
        lat = self.request.get('lat', None)
        lng = self.request.get('lng', None)

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
####End input checking####

        if not lat or not lng:
            url = 'https://maps.googleapis.com/maps/api/geocode/json?address='+zipcode+'&key=AIzaSyCGA86L8v4Lh-AUJHsKvQODP8SNsbTjYqg'
            location = json.loads(urllib2.urlopen(url).read())
            lat = str(location['results'][0]['geometry']['location']['lat'])
            lng = str(location['results'][0]['geometry']['location']['lng'])

        key = '71f6bcee6c068c552bf84460d5409'

        url = 'http://api.worldweatheronline.com/free/v2/past-weather.ashx'+ \
              '?key='+key+ \
              '&format=json'+ \
              '&q='+lat+','+lng
        today = json.loads(urllib2.urlopen(url).read())

        url = 'https://maps.googleapis.com/maps/api/timezone/json?key=AIzaSyCGA86L8v4Lh-AUJHsKvQODP8SNsbTjYqg' + \
              '&timestamp='+str(int(time.mktime(datetime.datetime.now().timetuple()))) + \
              '&location='+lat+','+lng
        timezone_data = json.loads(urllib2.urlopen(url).read())
        hour_offset = timezone_data['rawOffset'] / 3600

        if include_today: # compare today to yesterday
            yesterday_datetime = datetime.date.today() - datetime.timedelta(1) + datetime.timedelta(hours=hour_offset)
            url = 'http://api.worldweatheronline.com/free/v2/past-weather.ashx'+ \
                  '?key='+key+ \
                  '&format=json'+ \
                  '&q='+lat+','+lng+ \
                  '&date='+yesterday_datetime.strftime('%Y-%m-%d')
            yesterday = json.loads(urllib2.urlopen(url).read())

            response['today'] = today_forecast(yesterday, today)
            response['tonight'] = tonight_temp_forecast(yesterday, today)

        if include_tomorrow: #compare tomorrow to today
            tomorrow_datetime = datetime.date.today() + datetime.timedelta(1) + datetime.timedelta(hours=hour_offset)
            url = 'http://api.worldweatheronline.com/free/v2/weather.ashx'+ \
                  '?key='+key+ \
                  '&format=json'+ \
                  '&q='+lat+','+lng+ \
                  '&date='+tomorrow_datetime.strftime('%Y-%m-%d')
            tomorrow = json.loads(urllib2.urlopen(url).read())

            response['tomorrow'] = tomorrow_temp_forecast(today, tomorrow)
            response['tomorrow_night'] = tomorrow_night_temp_forecast(today, tomorrow)

        #LOCATION
        url = 'https://maps.googleapis.com/maps/api/geocode/json'+ \
              '?key=AIzaSyCGA86L8v4Lh-AUJHsKvQODP8SNsbTjYqg'+ \
              '&latlng='+lat+','+lng
        location = json.loads(urllib2.urlopen(url).read())

        response['city'] = search_location(location, 'locality')
        if search_location(location, 'country') not in ['US', 'USA']: #THEN THEY ARE A COMMUNIST
            response['state'] = search_location(location, 'country', param='long_name') # stockholm, sweden
        else:
            response['state'] = search_location(location, 'administrative_area_level_1')
        response['zip'] = search_location(location, 'postal_code')
        if response['zip'] == None:
            response['zip'] = '666'
        write(response)
        return # send the data


class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        template_values = {}
        self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([
    (r'/api', API),
    (r'/api/(.*)', API),
    ('/', MainHandler)
], debug=True)

