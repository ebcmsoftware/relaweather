# big thx to worldweatheronline api
# NOTE: ALL TEMPERATURES FARENHEIGHT, 
# ALL PRECIPITATION VALUES IN MILLIMETERS
# TODO: Day/night modularity and things

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

# hourly average for param (used for precipitation but modularity is cool i guess)
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

# generalized precipitation forecast, includes if skies are clear
# TODO: find if rain or snow. somehow. be smart. use ['weatherDesc']['value']?
# TODO: more adjectives
# TODO: CLEAR SKIES AND CLOUDS
# TODO: something about std dev (lambda) of rainfall, is it steady, inconsistent, big storm?
def precip_forecast(total_precip):
    # (hourly avg over 12 hrs) * 12 = total
    # total precipitation (in MM? doesnt seem right.) for today

    if total_precip == 0:
        return None
    if total_precip < 1.0:
        return random.choice(['some', 'a few']) + ' ' + random.choice(['drizzles', 'sprinkles'])
    elif 1.0 < total_precip < 5.0:
        return random.choice(['a little precipitation', 'some showers'])
    elif 5.0 < total_precip < 20.0: 
        return random.choice(['steady rain', 'quite a bit of rain'])
    else:
        return 'lots of rain'

# returns an adjective or little phrase about the temperature difference
# given the average temp so that it can use the right words
# TODO: do this more intelligently, based on region and maybe more criteria/randomized adjectives.
def hot_or_cold_adj(temp_diff, avg_temp):
    if temp_diff == 0:
        return ''

    if temp_diff < 0:
        if avg_temp < 30:
            return 'colder'
        elif 30 < avg_temp <= 50:
            return 'chillier'
        elif 50 < avg_temp <= 60:
            return 'cooler'
        elif 60 < avg_temp <= 80:
            return 'less warm'
        else:
            return 'less hot'

    if temp_diff > 0:
        if avg_temp < 30:
            return 'less cold'
        elif 30 < avg_temp <= 50:
            return 'less chilly'
        elif 50 < avg_temp <= 60:
            return 'less cool'
        elif 60 < avg_temp <= 80:
            return 'warmer'
        else:
            return 'hotter'

# returns a string describing the difference between temp_before and temp_after
def temp_forecast(temp_before, temp_after):
    temp_diff = temp_after - temp_before
    hot_or_cold = ''
    if temp_diff == 0:
        return 'about the same temperature as'
    hot_or_cold = hot_or_cold_adj(temp_diff, (temp_before + temp_after) / 2.0)
    temp_diff = abs(temp_diff)

    if temp_diff < 3:
        adj = random.choice(['a little', 'a bit', 'slightly', 'somewhat'])
    elif 3 < temp_diff < 7:
        return hot_or_cold + ' than'
    else:
        adj = random.choice(['noticeably', 'much', 'a lot', 'quite a bit', 'considerably', 'appreciably'])
    return adj + ' ' + hot_or_cold + ' than'


#5am-5pm - same thing just "is" rather than "will be"
def forecast_day(yesterday, today, tomorrow, verb):
    forecast_1 = forecast_2 = forecast_3 = ''
    today_max = float(today['data']['weather'][0]['maxtempF'])
    ###########################################################################
    # FORECAST 1 - "today is/will be" "yesterday"
    yesterday_max = float(yesterday['data']['weather'][0]['maxtempF'])
    temperature = temp_forecast(yesterday_max, today_max)

    total_precip= avg(today, 'precipMM') * 12.0
    precip = precip_forecast(total_precip)

    forecast_1 = 'today '+verb+' '+temperature+' yesterday'
    if precip:
        forecast_1 += ' with ' + precip
    ###########################################################################
    # FORECAST 2 - "tonight will be" "last night"
    # TODO <- night is very TODO
    pass
    ###########################################################################
    # FORECAST 3 - "tomorrow will be" "today"
    tomorrow_max = float(tomorrow['data']['weather'][0]['maxtempF'])
    temperature = temp_forecast(today_max, tomorrow_max)

    total_precip = avg(tomorrow, 'precipMM') * 12.0
    precip = precip_forecast(total_precip)

    forecast_3 = 'tomorrow will be '+temperature+' today'
    if precip:
        forecast_3 += ' with '+precip
    ###########################################################################
    return (forecast_1, forecast_2, forecast_3)


#5pm-5am
def forecast_night(yesterday, today, tomorrow, verb):
    forecast_1 = forecast_2 = forecast_3 = ''
    yesterday_max = float(yesterday['data']['weather'][0]['maxtempF'])
    ###########################################################################
    # FORECAST 1 - "tonight is" "last night"
    ###########################################################################
    # FORECAST 2 - "tomorrow will be" "yesterday"
    today_max = float(today['data']['weather'][0]['maxtempF'])
    temperature = temp_forecast(yesterday_max, today_max)

    total_precip = avg(today, 'precipMM') * 12.0
    precip = precip_forecast(total_precip)

    forecast_2 = 'tomorrow will be '+temperature+' yesterday'
    if precip:
        forecast_2 += ' with '+precip
    ###########################################################################
    # FORECAST 3 - "tomorrow night will be" "tonight"
    ###########################################################################
    return (forecast_1, forecast_2, forecast_3)


def forecast(yesterday, today, tomorrow, local_datetime):
    hour = (today_datetime - today_datetime.replace(hour=0,minute=0,second=0)).seconds / 3600.0

    if 5.0 < hour <= 11.0: # morning
        return forecast_day(yesterday, today, tomorrow, 'will be')
    elif 11.0 < hour <= 17.0: # day
        return forecast_day(yesterday, today, tomorrow, 'is')
    elif 17.0 < hour <= 23.0: # day
        return ('oh', 'oh2', 'oh3') #TODO remove this after implementing forecast
        return forecast_night(yesterday, today, tomorrow, 'will be')
    else: # night
        return ('oh', 'oh2', 'oh3') #TODO remove this after implementing forecast
        return forecast_night(yesterday, today, tomorrow, 'is')

# returns a string with today's forecast given json objects from WWO
# with weather for yesterday and today
def today_forecast(yesterday, today, today_datetime):
    today_max = float(today['data']['weather'][0]['maxtempF'])
    yesterday_max = float(yesterday['data']['weather'][0]['maxtempF'])
    temperature = temp_forecast(yesterday_max, today_max)

    total_precip = avg(today, 'precipMM') * 12.0
    precip = precip_forecast(total_precip)

    # TODO: what do we do if they access at 12:01am
    hour = (today_datetime - today_datetime.replace(hour=0,minute=0,second=0)).seconds / 3600.0
    if hour <= 11:
        verb = 'will be'
    elif hour <= 17:
        verb = 'is'
    else:
        verb = 'was'
    to_return = 'today ' + verb + ' ' + temperature + ' yesterday'
    if precip:
        to_return += ' with ' + precip
    return to_return

# returns a string with tomorrow's forecast given json objects from WWO
# with weather for today and tomorrow
def tomorrow_forecast(today, tomorrow):
    today_max = float(today['data']['weather'][0]['maxtempF'])
    tomorrow_max = float(tomorrow['data']['weather'][0]['maxtempF'])
    temperature = temp_forecast(today_max, tomorrow_max)

    total_precip = avg(tomorrow, 'precipMM') * 12.0
    precip = precip_forecast(total_precip)

    verb = 'will be'
    to_return = 'tomorrow ' + verb + ' ' + temperature + ' today'
    if precip:
        to_return += ' with ' + precip
    return to_return

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
# End input checking

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
        local_datetime = datetime.datetime.now() + datetime.timedelta(hours=hour_offset)

        if include_today: # compare today to yesterday
            yesterday_datetime = local_datetime - datetime.timedelta(1)
            url = 'http://api.worldweatheronline.com/free/v2/past-weather.ashx'+ \
                  '?key='+key+ \
                  '&format=json'+ \
                  '&q='+lat+','+lng+ \
                  '&date='+yesterday_datetime.strftime('%Y-%m-%d')
            yesterday = json.loads(urllib2.urlopen(url).read())

            response['today'] = today_forecast(yesterday, today, local_datetime)
            #response['tonight'] = tonight_temp_forecast(yesterday, today)

        if include_tomorrow: #compare tomorrow to today
            tomorrow_datetime = local_datetime + datetime.timedelta(1)
            url = 'http://api.worldweatheronline.com/free/v2/weather.ashx'+ \
                  '?key='+key+ \
                  '&format=json'+ \
                  '&q='+lat+','+lng+ \
                  '&date='+tomorrow_datetime.strftime('%Y-%m-%d')
            tomorrow = json.loads(urllib2.urlopen(url).read())

            response['tomorrow'] = tomorrow_forecast(today, tomorrow)
            #response['tomorrow_night'] = tomorrow_night_temp_forecast(today, tomorrow)

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

