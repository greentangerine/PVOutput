#!/usr/bin/env python3

# openweathermap.py

# read forecast from openweathermap.org

import json
import requests

debug=False

def get_openweathermap_data(sysapi, latitude, longitude, app_log=None):
    if sysapi is None:
        return

    payload = {'appid': sysapi, 
               'lat': str(latitude),
               'lon': str(longitude),
               'units': 'metric',
               'lang': 'en'
              }

    if debug:
        if app_log is not None:
            app_log.info(payload)

    url = 'https://api.openweathermap.org/data/2.5/onecall'

    try:
        response = requests.get(url, params=payload)
    except requests.exceptions.RequestException as e:
        if debug:
            if app_log is not None:
                app_log.error(e)

    if response.status_code == 200:
        str_response = response.content.decode("utf-8")
  
    if debug:
        if app_log is not None:
            app_log.info(str_response)
            app_log.info(response.url)

    return json.loads(str_response)


def get_openweathermap_historic_data(sysapi, latitude, longitude, date, app_log=None):
    if sysapi is None:
        return

    payload = {'appid': sysapi, 
               'lat': str(latitude),
               'lon': str(longitude),
               'units': 'metric',
               'lang': 'en',
               'dt': str(date)
              }

    if debug:
        if app_log is not None:
            app_log.info(payload)

    url = 'https://api.openweathermap.org/data/2.5/onecall/timemachine'

    try:
        response = requests.get(url, params=payload)
    except requests.exceptions.RequestException as e:
        if debug:
            if app_log is not None:
                app_log.error(e)

    if response.status_code == 200:
        str_response = response.content.decode("utf-8")
  
    if debug:
        if app_log is not None:
            app_log.info(str_response)
            app_log.info(response.url)

    return json.loads(str_response)


