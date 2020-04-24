#!/usr/bin/env python3

# weatherbit.py

# read forecast and write actuals to weatherbit.io

import json
import requests

import sys
sys.path.insert(0, '/home/pi/PVOutput')

# API keys etc.
from MyKeys import *

debug=False

def get_weatherbit_forecast(sysapi, latitude, longitude, days, app_log=None):
    if sysapi is None:
        return

    payload = {'key': sysapi, 
               'units': 'M',
               'lang': 'en',
               'lat': str(latitude),
               'lon': str(longitude),
               'days': str(days)
              }

    if debug:
        if app_log is not None:
            app_log.info(payload)

    url = 'https://api.weatherbit.io/v2.0/forecast/daily'

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


def get_weatherbit_current(sysapi, latitude, longitude, app_log=None):
    if sysapi is None:
        return

    payload = {'key': sysapi, 
               'units': 'M',
               'lang': 'en',
               'lat': str(latitude),
               'lon': str(longitude)
              }

    if debug:
        if app_log is not None:
            app_log.info(payload)

    url = 'https://api.weatherbit.io/v2.0/current'

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


