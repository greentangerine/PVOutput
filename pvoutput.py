#!/usr/bin/env python3

# pvoutput.py
# Pulls Solar and Home use data from your emoncms.org account and squirts the
# data up to PVOutput
#
# Also optionally uploads to solcast.com
#
# This can run on any internet host running Python3 and you should schedule 
# the script to run every 5 mins
# You may be able to change to talk to your internal emonpi instance if you 
# don't want it to go external.
#
# */5 * * * * /usr/bin/python3 /home/PVOutput/pvoutput_upload.py
#
# 5 mins is the shortest time period you can send to PVO (in donation mode),
# otherwise its 15 mins if you don't have a donation PVO account
# https://forum.pvoutput.org/c/donation-features
#
# As well as needing Python 3 installed you'll need to install the 
# following modules
# sudo pip3 install numpy
# sudo pip3 install pytz

import time
import datetime as dt
import json
import requests
import platform

import sys
sys.path.insert(0, '/home/pi/PVOutput')

from pytz import timezone
from solcast import post_solcast

# API keys etc.
from MyKeys import *


def get_emoncms_data(apikey, feed_id, period):
  if apikey is None:
    return

  text_values = ''
  payload = {'id': feed_id, 
             'apikey': apikey, 
             'skipmissing': 1,
             'start': unix_milli_start, 
             'end': unix_milli_end, 
             'interval': period}

  if debug:
    app_log.info(payload)
  header = {'content-type': 'application/json'}

  try:
    response = requests.get("http://emonpi/feed/data.json", 
                            params=payload, headers=header)
  except requests.exceptions.RequestException as e:
    if debug:
        app_log.error('Feed ID: %s', feed_id)
        app_log.error(e)

  if response.status_code == 200:
    str_response = response.content.decode("utf-8")
  
    if debug:
        app_log.info(str_response)
        app_log.info(response.url)

    print(str_response)
    mylist = json.loads(str_response)

    reading = 0
    count = 1
    total = 0

    for x in mylist: 
      reading = (x[1])
      total = total + int(reading)
      count = count + 1
      text_values = text_values + (str(int(reading))) + ', '

    count = count - 1

    if debug:
      app_log.info('Number of numbers pulled (count): %s', count)
      app_log.info('Number of numbers (total): %s', total)

    if count != 0 or total != 0:
      output = (int(total/count))
    else:
      output = 0

  else:
    output = 0

  return (output, text_values)


def post_pvoutput(apikey, sysids, gen, vrms, usage, temp, humidity, intemp):
  if apikey is None:
    return

  # may raise exceptions
  url = 'https://pvoutput.org/service/r2/addstatus.jsp'

  for i in range(len(sysids)):
    headers = {
      'X-Pvoutput-SystemId': str(sysids[i]),
      'X-Pvoutput-Apikey': str(apikey)
    }
    params = {
      'd': date,
      't': time,
      'v2': gen[i],
      'v5': str(temp),
      'v6': str(vrms),
      'v7': str(humidity),
      'v8': str(usage),
      'v12':str(intemp)
    }

    app_log.info('posting data to pvoutput')
    if debug:
      app_log.info(headers)
      app_log.info(params)
    resp = requests.post(url, headers=headers, data=params, timeout=10)
    if resp.status_code != 200:
      app_log.error(resp.status_code)
      app_log.error('pvoutput returned code %s', resp.status_code)
      app_log.error(resp.text)

  return


# configure logging ...
import logging
from logging.handlers import RotatingFileHandler

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

if platform.system() == 'Windows':
  # Windows current directory
  logFile = 'log.txt'
else:
  # Linux absolute path
  logFile = '/tmp/PVOutput.log'

my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, 
                                 backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)

app_log.info('-------------------------------------------------------------------------------')
app_log.info('logfile: %s', logFile)

debug=False
#debug=True

# EmonCMS.org details
FEED_ID_USE=17
FEED_ID_SOLAR=[4, 2, 3]
FEED_ID_VOLTS=10
FEED_ID_TEMP=20
FEED_ID_IN_TEMP=24
FEED_ID_HUMIDITY=21

# How many seconds between data points 
# (ie, EmonCMS updates every 10 seconds and PVOuput only accepts every 5 mins.... so using 10 seems to catch most of the 29/30 unique values)
INTERVAL_TX=10
# emonTH uses 60s intervals
INTERVAL_TH=60

# Time right now in milliseconds
unix_milli_end = int(round(time.time() * 1000))
# 5 minutes ago in milliseconds (PVOutput only accepts 5 minute updates)
unix_milli_start = ((unix_milli_end - 300000))
# If you need to change this to 15 mins then its 900,000

# Date for PVOutput 
date = time.strftime('%Y%m%d')
time = time.strftime('%R')


# Reset working variables
solar_gen = 0
home_usage = 0
raw_values = ''
solar = []
volts = 0
outside_temp = 0
inside_temp = 0
outside_humidity = 0
total_gen = 0

# Query the TH units ...
interval = INTERVAL_TH

# Get temperature figure from EmonCMS API
feed_id = FEED_ID_TEMP 
app_log.info('Getting temperature, feed id: %s', feed_id)
outside_temp, raw_values = get_emoncms_data(EMONPI_APIKEY, feed_id, interval)
if debug:
    app_log.info('Temperature Raw: %s', raw_values)

# Get humidity figure from EmonCMS API
feed_id = FEED_ID_HUMIDITY 
app_log.info('Getting humidity, feed id: %s', feed_id)
outside_humidity, raw_values = get_emoncms_data(EMONPI_APIKEY, feed_id, interval)
if debug:
    app_log.info('Temperature Raw: %s', raw_values)

# Query the TX units ...
interval = INTERVAL_TX

# Get voltage figure from EmonCMS API
feed_id = FEED_ID_VOLTS 
app_log.info('Getting voltage, feed id: %s', feed_id)
volts, raw_values = get_emoncms_data(EMONPI_APIKEY, feed_id, interval)
if debug:
    app_log.info('Voltage Raw: %s', raw_values)

# Get inside temperature figure from EmonCMS API
feed_id = FEED_ID_IN_TEMP
app_log.info('Getting inside temp, feed id: %s', feed_id)
inside_temp, raw_values = get_emoncms_data(EMONPI_APIKEY, feed_id, interval)
if debug:
    app_log.info('Inside temperature Raw: %s', raw_values)

# Get Home Usage figure from EmonCMS API
feed_id = FEED_ID_USE 
app_log.info('Getting Home Use, feed id: %s', feed_id)
home_usage, raw_values = get_emoncms_data(EMONPI_APIKEY, feed_id, interval)
if debug:
    app_log.info('Home Usage Raw: %s', raw_values)

# Get Solar Generation figure from EmonCMS API
for feed_id in FEED_ID_SOLAR:
  app_log.info('Getting Solar Use, feed id: %s', feed_id)
  solar_gen, raw_values = get_emoncms_data(EMONPI_APIKEY, feed_id, interval)
  solar.append(solar_gen)
  total_gen = total_gen + solar_gen
  if debug:
      app_log.info('Solar Usage Raw: %s', raw_values)

app_log.info('Solar W: %s', total_gen)
app_log.info('Usage W: %s', home_usage)
app_log.info('Voltage V: %s', volts)
app_log.info('Outside Temp C: %s', outside_temp)
app_log.info('Inside Temp C: %s', inside_temp)
app_log.info('Outside Humidity P: %s', outside_humidity)

if platform.system() == 'Windows':
  # Windows current directory
  app_log.info('i am on Windows, no uploading')
else:
  # Punt collected data up to PVPoutput.org
  post_pvoutput(PVO_API, PVO_SYSID, solar, volts, home_usage, 
                outside_temp, outside_humidity, inside_temp)
  post_solcast(SOLCAST_APIKEY, SOLCAST_SYSID, total_gen,
               dt.datetime.utcnow().isoformat() + 'Z',
               'PT5M', app_log)

