#big thx to worldweatheronline api

import os
import json
import jinja2
import random
import logging
import webapp2
import urllib2
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
def get_avg(data, param, night=False):
    avg = 0.0
    if night:
        for i in range(4): #4*3 = 12. things are measured in 3hr periods, 12hrs is half the day.
            avg += float(data['data']['weather'][0]['hourly'][(i+5) % 8][param]) # 5, 6, 7, 0
        avg /= 12.0
        return avg
    else:
        for i in range(4): #4*3 = 12. things are measured in 3hr periods, 12hrs is half the day.
            avg += float(data['data']['weather'][0]['hourly'][i+1][param]) # 1, 2, 3, 4
        avg /= 12.0
        return avg

#TODO: find if rain or snow. somehow. be smart
def get_tomorrow_precip(tomorrow):
    tomorrow_precip = get_avg(tomorrow, 'precipMM') * 12.0 # (hourly avg over 12 hrs) * 12 = total
    return tomorrow_precip

def get_tomorrow_night_precip(tomorrow):
    tomorrow_night_precip = get_avg(tomorrow, 'precipMM', night=True) * 12.0
    return tomorrow_night_precip

def get_tomorrow_night_temp(today, tomorrow):
    today_min = today['data']['weather'][0]['mintempF']
    tomorrow_min = tomorrow['data']['weather'][0]['mintempF']
    return '(today_min - tomorrow_min): %f' %(float(today_min) - float(tomorrow_min))

def get_tomorrow_temp(today, tomorrow):
    today_max = today['data']['weather'][0]['maxtempF']
    tomorrow_max = tomorrow['data']['weather'][0]['maxtempF']
    return '(today_max - tomorrow_max): %f' %(float(today_max) - float(tomorrow_max))


def get_tonight_precip(today):
    today_precip = get_avg(today, 'precipMM', night=True) * 12.0 
    return today_precip

def get_tonight_temp(yesterday, today):
    today_min = today['data']['weather'][0]['mintempF']
    yesterday_min = yesterday['data']['weather'][0]['mintempF']
    return '(today_min - yesterday_min): %f' %(float(today_min) - float(yesterday_min))

def get_today_precip(today):
    today_precip = get_avg(today, 'precipMM') * 12.0 # (hourly avg over 12 hrs) * 12 = total
    #TODO: find thresholds. find rain or snow or hail or...
    if today_precip == 0:
        return None
    if today_precip < 0.1:
        return random.choice(['occasionally drizzly', 'with scattered rain'])
    elif today_precip < 0.2:
        return random.choice(['with a little precipitation', 'with slight rain', 'with some showers'])
    else: 
        return 'rainy'

def get_today_temp_forecast(yesterday, today):
    today_max = today['data']['weather'][0]['maxtempF']
    yesterday_max = yesterday['data']['weather'][0]['maxtempF']
    today_diff = float(today_max) - float(yesterday_max)
    logging.info(today_diff)
    hot_or_cold = ''
    if today_diff == 0:
        return 'today is gonna be about the same temperature as yesterday'
    if today_diff > 0:
        hot_or_cold = 'hotter'
    else:
        hot_or_cold = 'colder'
    today_diff = abs(today_diff)
    # begin CSC
    if today_diff < 3:
        adj = random.choice(['a little ', 'a bit ', 'slightly '])
        return 'today is ' + adj + hot_or_cold + ' than yesterday'
    elif today_diff < 6:
        adj = random.choice([' ', 'noticeably '])
        return 'today is ' + adj + hot_or_cold + ' than yesterday'
    else:
        adj = random.choice(['a fuck ton '])
        return 'today is ' + adj + hot_or_cold + ' than yesterday'

def get_today_forecast(yesterday, today):
    temperature = get_today_temp_forecast(yesterday, today)
    precip = get_today_precip(today)
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

        if include_today: # compare today to yesterday
            yesterday_datetime = datetime.date.today() - datetime.timedelta(1)
            url = 'http://api.worldweatheronline.com/free/v2/past-weather.ashx'+ \
                  '?key='+key+ \
                  '&format=json'+ \
                  '&q='+lat+','+lng+ \
                  '&date='+yesterday_datetime.strftime('%Y-%m-%d')
            yesterday = json.loads(urllib2.urlopen(url).read())

            response['today'] = get_today_forecast(yesterday, today)
            response['tonight'] = get_tonight_temp(yesterday, today)

        if include_tomorrow: #compare tomorrow to today
            tomorrow_datetime = datetime.date.today() + datetime.timedelta(1)
            url = 'http://api.worldweatheronline.com/free/v2/weather.ashx'+ \
                  '?key='+key+ \
                  '&format=json'+ \
                  '&q='+lat+','+lng+ \
                  '&date='+tomorrow_datetime.strftime('%Y-%m-%d')
            tomorrow = json.loads(urllib2.urlopen(url).read())

            response['tomorrow'] = get_tomorrow_temp(today, tomorrow)
            response['tomorrow_night'] = get_tomorrow_night_temp(today, tomorrow)

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

