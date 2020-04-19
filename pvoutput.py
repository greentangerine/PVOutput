#!/usr/bin/env python

# pvoutput_upload.py
# Pulls Solar and Home use data from your emoncms.org account and squirts the data up to PVOutput
#
# This can run on any internet host running Python3 and you should schedule the script to run every 5 mins
# You may be able to change to talk to your internal emonpi instance if you don't want it to go external.
#
# */5 * * * * /usr/bin/python3 /home/PVOutput/pvoutput_upload.py
#
# 5 mins is the shortest time period you can send to PVO (in donation mode), otherwise its 15 mins if you don't have a donation PVO account
# https://forum.pvoutput.org/c/donation-features
#
# Based on your longtitude and latitude the script also pulls down current tempearture (from DarkSky) and uses Pysolar to calculate the current sun angle.
# Use a website like https://www.latlong.net/ to calculate your lon and lat
#
# As well as needing Python 3 installed you'll need to install the following modules
# sudo pip3 install pysolar
# sudo pip3 install numpy
# sudo pip3 install pytz

import time
import datetime
import json
import requests
import platform
import sys

from pysolar.solar import *
from pytz import timezone

##############################################################

def get_emoncms_data(FEED_ID, PERIOD):

  TEXT_VALUES = ''
  payload = {'id': FEED_ID, 'apikey': EMONPI_APIKEY, 'start': UNIX_MILLI_START, 'end': UNIX_MILLI_END, 'interval': PERIOD}

  if DEBUG ==1:
    app_log.info(payload)
  header = {'content-type': 'application/json'}

  try:
    response = requests.get("http://emonpi/feed/data.json", params=payload, headers=header)
  except requests.exceptions.RequestException as e:
    if DEBUG ==1:
        app_log.error('Feed ID: %s', FEED_ID)
        app_log.error(e)

  if response.status_code == 200:
    str_response = response.content.decode("utf-8")
  
    if DEBUG ==1:
        app_log.info(str_response)
        app_log.info(response.url)

    mylist = json.loads(str_response)

    READING = 0
    COUNT = 1
    TOTAL = 0

    for x in mylist: 
      #print (COUNT,x)
      READING = (x[1])
      TOTAL = TOTAL + READING
      COUNT = COUNT + 1
      TEXT_VALUES = TEXT_VALUES + (str(int(READING))) + ', '

    #print ()
    COUNT = COUNT - 1
    #print (COUNT)
    #print (TOTAL)
    #OUTPUT = (int(TOTAL/COUNT))
    #print (OUTPUT)


    app_log.info('Number of numbers pulled (COUNT): %s', COUNT)
    app_log.info('Number of numbers (TOTAL): %s', TOTAL)

    if COUNT != 0 or TOTAL != 0:
      OUTPUT = (int(TOTAL/COUNT))
    else:
      OUTPUT = 0

  else:
    OUTPUT = 0

  return (OUTPUT, TEXT_VALUES)

#########################################################################

def post_pvoutput(SYSIDS, GEN, VRMS, USAGE, TEMP, HUMIDITY, INTEMP): # may raise exceptions
  url = 'https://pvoutput.org/service/r2/addstatus.jsp'

  for i in range(len(SYSIDS)):
    headers = {
      'X-Pvoutput-SystemId': str(SYSIDS[i]),
      'X-Pvoutput-Apikey': str(PVO_API)
    }
    params = {
      'd': DATE,
      't': TIME,
      'v2': GEN[i],
      'v5': str(TEMP),
      'v6': str(VRMS),
      'v7': str(HUMIDITY),
      'v8': str(USAGE),
      'v12':str(INTEMP)
    }

    app_log.info('posting data to pvoutput')
    if DEBUG ==1:
      app_log.info(headers)
      app_log.info(params)
    resp = requests.post(url, headers=headers, data=params, timeout=10)
    if resp.status_code != 200:
      app_log.error(resp.status_code)
      app_log.error('pvoutput returned code %s', resp.status_code)
      app_log.error(resp.text)

  return


##########################################################################


import logging
from logging.handlers import RotatingFileHandler

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

if platform.system() == 'Windows':
  # Windows current directory
  logFile = 'log.txt'
else:
  # Linux absolute path
  logFile = '/home/pi/PVOutput/log.txt'

my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)

app_log.addHandler(my_handler)

app_log.info('-----------------------------------------------------------------------------------------------------------------------------')
app_log.info('logfile: %s', logFile)

##############################################################################

DEBUG=1

# PVOutput.org details
PVO_API='a0cc35b33a79ef4f68c852aeca2c986049aef769' #your PVOutput.org API key
# PVOutput system id order needs to match the feed order below ...
PVO_SYSID=[3642, 18483, 32437]

# EmonCMS.org details
EMONPI_APIKEY='f8a318181e71fe81fac90776ce9e1dcf'
FEED_ID_USE=17
FEED_ID_SOLAR=[4, 2, 3]
FEED_ID_VOLTS=10
FEED_ID_TEMP=20
FEED_ID_IN_TEMP=23
FEED_ID_HUMIDITY=21

# How many seconds between data points 
# (ie, EmonCMS updates every 10 seconds and PVOuput only accepts every 5 mins.... so using 10 seems to catch most of the 29/30 unique values)
INTERVAL_TX=10
# emonTH uses 60s intervals
INTERVAL_TH=60

# Time right now in milliseconds
UNIX_MILLI_END=int(round(time.time() * 1000))
# 5 minutes ago in milliseconds (PVOutput only accepts 5 minute updates)
UNIX_MILLI_START=((UNIX_MILLI_END-300000))
# If you need to change this to 15 mins then its 900,000


# Date for PVOutput 
DATE = time.strftime('%Y%m%d')
TIME = time.strftime('%R')

#print (UNIX_MILLI_START)
#print (UNIX_MILLI_END)

# Reset working variables
SOLAR_GEN = 0
HOME_USAGE = 0
RAW_VALUES = ''
SOLAR = []
VOLTS = 0
OUTSIDE_TEMP = 0
INSIDE_TEMP = 0
OUTSIDE_HUMIDITY = 0

INTERVAL=INTERVAL_TH

# Get temperature figure from EmonCMS API
FEED_ID = FEED_ID_TEMP 
app_log.info('Getting temperature, feed id: %s', FEED_ID)
OUTSIDE_TEMP, RAW_VALUES = get_emoncms_data(FEED_ID, INTERVAL)
if DEBUG ==1:
    app_log.info('Temperature Raw: %s', RAW_VALUES)
#print (RAW_VALUES)

# Get humidity figure from EmonCMS API
FEED_ID = FEED_ID_HUMIDITY 
app_log.info('Getting humidity, feed id: %s', FEED_ID)
OUTSIDE_HUMIDITY, RAW_VALUES = get_emoncms_data(FEED_ID, INTERVAL)
if DEBUG ==1:
    app_log.info('Temperature Raw: %s', RAW_VALUES)
#print (RAW_VALUES)

INTERVAL=INTERVAL_TX

# Get voltage figure from EmonCMS API
FEED_ID = FEED_ID_VOLTS 
app_log.info('Getting voltage, feed id: %s', FEED_ID)
VOLTS, RAW_VALUES = get_emoncms_data(FEED_ID, INTERVAL)
if DEBUG ==1:
    app_log.info('Voltage Raw: %s', RAW_VALUES)
#print (RAW_VALUES)

# Get inside temperature figure from EmonCMS API
FEED_ID = FEED_ID_IN_TEMP
app_log.info('Getting voltage, feed id: %s', FEED_ID)
INSIDE_TEMP, RAW_VALUES = get_emoncms_data(FEED_ID, INTERVAL)
if DEBUG ==1:
    app_log.info('Inside temperature Raw: %s', RAW_VALUES)
#print (RAW_VALUES)

# Get Home Usage figure from EmonCMS API
FEED_ID = FEED_ID_USE 
app_log.info('Getting Home Use, feed id: %s', FEED_ID)
HOME_USAGE, RAW_VALUES = get_emoncms_data(FEED_ID, INTERVAL)
if DEBUG == 1:
    app_log.info('Home Usage Raw: %s', RAW_VALUES)
#print (RAW_VALUES)

# Get Solar Generation figure from EmonCMS API
for FEED_ID in FEED_ID_SOLAR:
  app_log.info('Getting Solar Use, feed id: %s', FEED_ID)
  SOLAR_GEN, RAW_VALUES = get_emoncms_data(FEED_ID, INTERVAL)
  SOLAR.append(SOLAR_GEN)
  if DEBUG ==1:
      app_log.info('Solar Usage Raw: %s', RAW_VALUES)
  #print (RAW_VALUES)

#print ()
#print (DATE)
#print (TIME)
#print ()
#print ('Solar: ',SOLAR)
#print ('Usage: ',HOME_USAGE)
#print ('Volts: ',VOLTS)
#print ('Temp: ',OUTSIDE_TEMP)
#print ('Temp: ',INSIDE_TEMP)
#print ('Humidity: ',OUTSIDE_HUMIDITY)


app_log.info('Solar W: %s', SOLAR_GEN)
app_log.info('Usage W: %s', HOME_USAGE)
app_log.info('Voltage V: %s', VOLTS)
app_log.info('Outside Temp C: %s', OUTSIDE_TEMP)
app_log.info('Inside Temp C: %s', INSIDE_TEMP)
app_log.info('Outside Humidity P: %s', OUTSIDE_HUMIDITY)

if platform.system() == 'Windows':
  # Windows current directory
  app_log.info('i am on Windows, no uploading')
else:
  # Punt collected data up to PVPoutput.org
  post_pvoutput(PVO_SYSID, SOLAR, VOLTS, HOME_USAGE, OUTSIDE_TEMP, OUTSIDE_HUMIDITY, INSIDE_TEMP)
  #print ('Funchi ...')

