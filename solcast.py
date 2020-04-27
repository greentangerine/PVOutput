#!/usr/bin/env python3

# solcast.py

# read forecast and write actuals to solcast.com

import json
import requests

debug=False

def post_solcast(sysapi, sysid, gen, end_time, period, app_log=None):
    # may raise exceptions
    """ Post generation to solcast.com.

        Expects a vaild API key and system ID.

        Generation is the average for the period specified in Watts
    """

    if sysapi is None:
        return

    url = 'https://api.solcast.com.au/rooftop_sites/' + str(sysid) +\
             '/measurements'

    headers = { 'Authorization': 'Bearer ' + str(sysapi),
                'Content-Type': 'application/json' }

    paramsStr = { "measurement": 
                  { "period_end": end_time,
                    "period": period,
                    "total_power": (gen / 1000)}}

    params = json.dumps(paramsStr)

    if app_log is not None:
        app_log.info('posting data to solcast')
        if debug:
            app_log.info(headers)
            app_log.info(params)

    resp = requests.post(url, headers=headers, data=params, timeout=10)
    if resp.status_code != 200:
        if app_log is not None:
            app_log.error(resp.status_code)
            app_log.error('pvoutput returned code %s', resp.status_code)
            app_log.error(resp.text)

    return


def get_solcast_forecast(sysapi, sysid, app_log=None):
    if sysapi is None:
        return

    payload = {'api_key': sysapi, 'format': 'json'}

    if debug:
        if app_log is not None:
            app_log.info(payload)

    url = 'https://api.solcast.com.au/rooftop_sites/' + str(sysid) +\
             '/forecasts'
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


def get_solcast_estimated_actuals(sysapi, sysid, app_log=None):
    if sysapi is None:
        return

    payload = {'api_key': sysapi, 'format': 'json'}

    if debug:
        if app_log is not None:
            app_log.info(payload)

    url = 'https://api.solcast.com.au/rooftop_sites/' + str(sysid) +\
             '/estimated_actuals'
    try:
        response = requests.get(url, params=payload)
    except requests.exceptions.RequestException as e:
        if debug:
            if app_log is not None:
                app_log.error(e)

    if response.status_code == 200:
        str_response = response.content.decode("utf-8")
  
    if app_log is not None:
        if debug:
            app_log.info(str_response)
            app_log.info(response.url)

    return json.loads(str_response)


