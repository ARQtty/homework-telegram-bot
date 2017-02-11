import urllib.request as req
import json

def getWeather():
    city = 'Saint-Petersburg'
    lang = 'en'
    weatherEmojs  = {'Clouds':'\U00002601', 'Mist': '\U0001F301', 'Snow': '\U00002744', 'Clear': '\U0001F5FB', 'Rain': '\U00002614', 'Thunderstorm':'\U000026A1', 'Drizzle':'\U00002614'}
    statEms = {'tmp':'\U0001F4C8','prs':'\U0001F4AD','hyd':'\U0001F4A7','wnd':'\U0001F343','inf':'\U00002139'}
    url = "http://api.openweathermap.org/data/2.5/weather?q="+city+"&mode=json&units=metric&appid=6151f42fb82c1ab87863da29465b594b&lang="+lang
    weatherMsg = '\n\nI have prepared a forecast that the weather did not catch you by surprise ' + statEms['inf'] + '\n\nAt this moment:\n'
    
    with req.urlopen(url) as f:
        json_string = f.read().decode("utf-8")
        parsed_json = json.loads(json_string)
        sky = parsed_json["weather"][0]['main']
        sky_deskr = parsed_json["weather"][0]['description']
        temp = str(parsed_json['main']['temp'])
        hyd = str(parsed_json['main']['humidity']) + '%'
        pressure = parsed_json['main']['pressure']
        windSpeed = str(parsed_json['wind']['speed']) + ' m/s'

    # Normal in my city: 103500-102000 Pascals
    if pressure < 1020 and pressure > 1003: 
        pressure = 'fine'
    elif pressure < 1003 and pressure > 993:
        pressure = 'below standard'
    elif pressure < 993:
    	pressure = 'low'
    elif pressure > 1020 and pressure < 1030:
        pressure = 'above the standard'
    elif pressure > 1030:
    	pressure = 'hight'
    try:
        sk_em = weatherEmojs[sky]
    except:
        sk_em = weatherEmojs['Clouds']

    weatherMsg += (statEms['tmp']+" Temperature: "+temp+" C\n"
                           +sk_em+" There is "+sky_deskr+" outdoors\n"
                  +statEms['prs']+" Pressure is "+pressure+"\n"
                  +statEms['hyd']+" Air humidity: "+hyd+"\n"
                  +statEms['wnd']+" Wind speed: "+windSpeed)
    weatherMsg += '''\n\nDon't be late to school\U00002764'''
    return weatherMsg

#print(getWeather())