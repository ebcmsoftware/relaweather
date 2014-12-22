# big thx to worldweatheronline api
# NOTE: ALL TEMPERATURES FARENHEIGHT
# NOTE: ALL PRECIPITATION VALUES IN MILLIMETERS

############## SETUP #############################################################

import os
import json
import time
import jinja2
import random
import urllib
import logging
import urllib2
import webapp2
import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

############## FUNCTIONS #############################################################

# hourly average for param (used for precipitation but modularity is cool i guess)
# data should be numerical.
def avg(weather_data, param)
    avg = 0.0
    for datapoint in weather_data[param]:
        avg += float(datapoint)
    avg /= 12.0 #TODO: is this divided by 12? or 4? is the "precipMM" over that 3hr period? I can't find anywhere on the docs that says it is, but this is what it seems like?
    return avg


# # TODO: min temp vs getting "tonight's" low temp?!
# def get_temp(time):
#     if night:
#         #TODO: Do this intelligently. Need tomorrow's data? But definitely don't look at midnight-6am of the current day.
#         return float(time['data']['weather'][0]['mintempF'])
#     else:
#         return float(time['data']['weather'][0]['maxtempF'])


def cloud_forecast(cloud_percent):
    if cloud_percent < 25:
        return random.choice(['clear skies', 'few clouds'])
    if cloud_percent < 75:
        return random.choice(['partly cloudy skies', 'some clouds'])
    if cloud_percent < 90:
        return random.choice(['mostly cloudy skies', 'many clouds', 'cloud cover'])
    return random.choice(['overcast', 'cloudy skies'])


def rain_forecast(total_precip):
    if total_precip <= 8:
        return random.choice(['some', 'a few']) + ' ' + random.choice(['drizzles', 'sprinkles'])
    if total_precip <= 20:
        return random.choice(['a little precipitation', 'some showers'])
    if total_precip <= 40: 
        return random.choice(['steady rain', 'quite a bit of rain'])
    else:
        return 'lots of rain'


def snow_forecast(total_precip):
    if total_precip <= 25: # inch of snow
        return random.choice(['some', 'a few']) + ' ' + random.choice(['flurries', 'light snow showers'])
    if total_precip <= 125: 
        return random.choice(['a little precipitation', 'some snow showers'])
    if total_precip <= 300: 
        return random.choice(['steady snow', 'quite a bit of snow'])
    else:
        return 'lots of snow'


# generalized precipitation forecast, includes if skies are clear
# TODO: find if rain or snow. somehow. be smart. use ['weatherDesc']['value']?
# TODO: something about std dev (lambda) of rainfall, is it steady, inconsistent, big storm?
def precip_forecast(total_precip, cloud_percent, temp):    
    if total_precip == 0:
        return cloud_forecast(cloud_percent)
    if temp >= 32: # naive snow decision
        return rain_forecast(total_precip)
    else: 
        return snow_forecast(total_precip)


# returns an adjective or little phrase about the temperature difference
# given the average temp so that it can use the right words
# TODO: do this more intelligently, based on region and maybe more criteria/randomized adjectives.
def hot_or_cold_adj(temp_diff, avg_temp):
    if temp_diff == 0:
        return ''

    if temp_diff < 0:
        if avg_temp <= 30:
            return 'colder'
        if 30 < avg_temp <= 50: # joined inequalities for readability
            return 'chillier'
        if 50 < avg_temp <= 60:
            return 'cooler'
        if 60 < avg_temp <= 80:
            return 'less warm'
        if avg_temp > 80:
            return 'less hot'

    if temp_diff > 0:
        if avg_temp < 30:
            return 'less cold'
        if 30 < avg_temp <= 60:
            return 'less chilly'
        #if 50 < avg_temp <= 60: #commented it out. "tomorrow will be much less cool than today" just doesn't sound right to me. feel free to add it back in or tweak.
        #    return 'less cool'
        if 60 < avg_temp <= 80:
            return 'warmer'
        if avg_temp > 80:
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


def get_forecast_data(last, current):
    last_temp = last['temp']
    now_temp = current['temp']

    total_precip = avg(current, 'precipMM') * 12.0
    cloud_percent = avg(current, 'cloudcover')

    temperature = temp_forecast(last_temp, now_temp)
    precip = precip_forecast(total_precip, cloud_percent, now_temp)

    return (temperature, precip)


def forecast_day(weather_data, verb):
    (tempdata, precipdata) = get_forecast_data(data['yesterday'], data['today'])
    forecast_1 = 'today ' + verb + ' ' + tempdata + ' yesterday with ' + precipdata

    (tempdata, precipdata) = get_forecast_data(data['yesterday_night'], data['tonight'])
    forecast_2 = 'tonight will be ' + tempdata + ' last night with ' + precipdata

    (tempdata, precipdata) = get_forecast_data(data['today'], data['tomorrow'])
    forecast_3 = 'tomorrow will be ' + tempdata + ' today with ' + precipdata

    return [forecast_1, forecast_2, forecast_3]


def forecast_night(data, verb):
    (tempdata, precipdata) = get_forecast_data(data['yesterday_night'], data['tonight'])
    forecast_1 = 'tonight ' + verb + ' ' + tempdata + ' last night with ' + precipdata

    (tempdata, precipdata) = get_forecast_data(data['today'], data['tomorrow'])
    forecast_2 = 'tomorrow will be ' + tempdata + ' today was with ' + precipdata #TODO: yesterday?!

    (tempdata, precipdata) = get_forecast_data(data['tonight'], data['tomorrow_night'])
    forecast_3 = 'tomorrow night will be ' + tempdata + ' tonight with ' + precipdata

    return [forecast_1, forecast_2, forecast_3]


def forecast(weather_data, local_datetime):
    hour = (local_datetime - local_datetime.replace(hour=0,minute=0,second=0)).seconds / 3600.0

    if 4.0 < hour <= 7.0: # 4am to 7am
        return forecast_day(weather_data, 'will be') + [1]
    elif 7.0 < hour <= 16.0: # 7am to 4pm
        return forecast_day(weather_data, 'is') + [2]
    elif 16.0 < hour <= 19.0: # 4pm to 7pm
        return forecast_night(weather_data, 'will be') + [3]
    else: # 7pm to 4am
        return forecast_night(weather_data, 'is') + [4]


def search_location(location, address_component, param='short_name'):
    components = location['results'][0]['address_components']
    for component in components:
        if address_component in component['types']:
            return component[param]

######### API/SERVER LOGIC ###############################################################

class API(webapp2.RequestHandler):
    def max_temp(data):
        return float(data['data']['weather'][0]['maxtempF'])

    def avg_night_temp(before, after):
        return (
            float(before['data']['weather'][0]['hourly'][-1]['FeelsLikeF']) + 
            float(after['data']['weather'][0]['hourly'][0]['FeelsLikeF'])
               ) / 2.0

    def arr_day(data, param):
        hourly = data['data']['weather'][0]['hourly']
        arr = []
        for datapt in hourly:
            if 600 < float(datapt['time']) <= 1800:
                arr.append(datapt[param])
        return arr

    def arr_night(before, after, param):
        hourly_before = before['data']['weather'][0]['hourly']
        hourly_after = after['data']['weather'][0]['hourly']
        arr = []
        for datapt in hourly_before:
            if float(datapt['time']) > 1800:
                arr.append(datapt[param])
        for datapt in hourly_after:
            if float(datapt['time']) <= 600:
                arr.append(datapt[param])
        return arr

    def get(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT'

        # Writes a dict to the response
        def write(response):
            self.response.write(json.dumps(response, separators=(',',':'), sort_keys=True))

# Error checking and input validation
        response = {}

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

        # get zip code from goggle, turn into lat and lng
        if not lat or not lng:
            url = 'https://maps.googleapis.com/maps/api/geocode/json?address='+zipcode+'&key=AIzaSyCGA86L8v4Lh-AUJHsKvQODP8SNsbTjYqg'
            location = json.load(urllib.urlopen(url))
            lat = str(location['results'][0]['geometry']['location']['lat'])
            lng = str(location['results'][0]['geometry']['location']['lng'])

        key = '71f6bcee6c068c552bf84460d5409' #weather key

        # TODAY
        url = 'https://maps.googleapis.com/maps/api/timezone/json?key=AIzaSyCGA86L8v4Lh-AUJHsKvQODP8SNsbTjYqg' + \
              '&timestamp='+str(int(time.mktime(datetime.datetime.now().timetuple()))) + \
              '&location='+lat+','+lng
        timezone_data = json.load(urllib.urlopen(url))
        hour_offset = timezone_data['rawOffset'] / 3600
        local_datetime = datetime.datetime.now() + datetime.timedelta(hours=hour_offset)
        url = 'http://api.worldweatheronline.com/free/v2/past-weather.ashx?key='+key+'&format=json&q='+lat+','+lng
        today = json.load(urllib.urlopen(url))

        # YESTERDAY
        yesterday_datetime = local_datetime - datetime.timedelta(1)
        url = 'http://api.worldweatheronline.com/free/v2/past-weather.ashx?key='+key+'&format=json&q='+lat+','+lng+'&date='+yesterday_datetime.strftime('%Y-%m-%d')
        yesterday = json.load(urllib.urlopen(url))

        # TOMORROW
        tomorrow_datetime = local_datetime + datetime.timedelta(1)
        url = 'http://api.worldweatheronline.com/free/v2/weather.ashx?key='+key+'&format=json&q='+lat+','+lng+'&date='+tomorrow_datetime.strftime('%Y-%m-%d')
        tomorrow = json.load(urllib.urlopen(url))

        # DAY AFTER TOMORROW
        tomorrow2_datetime = local_datetime + datetime.timedelta(2)
        url = 'http://api.worldweatheronline.com/free/v2/weather.ashx?key='+key+'&format=json&q='+lat+','+lng+'&date='+tomorrow2_datetime.strftime('%Y-%m-%d')
        tomorrow2 = json.load(urllib.urlopen(url))

        weather_data = {}
        weather_data['yesterday'] = {
            'temp':max_temp(yesterday),
            'cloudcover':arr_day(yesterday, 'cloudcover'),
            'precipMM':arr_day(yesterday, 'precipMM')
            }
        weather_data['last_night'] = {
            'temp':avg_night_temp(yesterday, today),
            'cloudcover':arr_night(yesterday, today, 'cloudcover'),
            'precipMM':arr_night(yesterday, today, 'precipMM')
            }
        weather_data['today'] = {
            'temp':max_temp(today),
            'cloudcover':arr_day(today, 'cloudcover'),
            'precipMM':arr_day(today, 'precipMM')
            }
        weather_data['tonight'] = {
            'temp':avg_night_temp(today, tomorrow),
            'cloudcover':arr_night(today, tomorrow, 'cloudcover'),
            'precipMM':arr_night(today, tomorrow, 'precipMM')
            }
        weather_data['tomorrow'] = {
            'temp':max_temp(tomorrow),
            'cloudcover':arr_day(tomorrow, 'cloudcover'),
            'precipMM':arr_day(tomorrow, 'precipMM')
            }
        weather_data['tomorrow_night'] = {
            'temp':avg_night_temp(tomorrow, tomorrow2),
            'cloudcover':arr_night(tomorrow, tomorrow2, 'cloudcover'),
            'precipMM':arr_night(tomorrow, tomorrow2, 'precipMM')
            }

        minutes = (local_datetime - local_datetime.replace(hour=0,minute=0,second=0)).seconds / 60
        random.seed(minutes / 10) # change random answers every 10 minutes. so refreshing doesnt change answers that that frequently. divide by n to change every n minutes.
        [forecast_1, forecast_2, forecast_3, data_type] = forecast(weather_data, local_datetime)

        response['current'] = forecast_1
        response['next'] = forecast_2
        response['next_next'] = forecast_3
        response['data_type'] = data_type

        #LOCATION
        url = 'https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyCGA86L8v4Lh-AUJHsKvQODP8SNsbTjYqg&latlng='+lat+','+lng
        location = json.load(urllib.urlopen(url))

        response['city'] = search_location(location, 'locality')
        if search_location(location, 'country') not in ['US', 'USA']: # THEN THEY ARE A COMMUNIST
            response['state'] = search_location(location, 'country', param='long_name') # ex: stockholm, sweden
        else:
            response['state'] = search_location(location, 'administrative_area_level_1')
        response['zip'] = search_location(location, 'postal_code')
        if response['zip'] == None:
            response['zip'] = '666'

        write(response)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        template_values = {}
        self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([
    ('/api', API),
    ('/', MainHandler)
], debug=True)
