#!/usr/bin/env python3

# solcast_test.py

# read forecast etc.

import datetime as dt
from dateutil.parser import isoparse

import sys
sys.path.insert(0, '/home/pi/PVOutput')

# API keys etc.
from MyKeys import *
from solcast import get_solcast_forecast, get_solcast_estimated_actuals

result_forecast = get_solcast_forecast(SOLCAST_APIKEY, SOLCAST_SYSID)

try:
    estimates = result_forecast['forecasts']
    #print(estimates)
except:
    print("No forecast!")
    quit()

pv_estimate = 0
pv_estimate10 = 0
pv_estimate90 = 0
one_day = dt.datetime.now(dt.timezone.utc).date() + dt.timedelta(days=1)

for period in estimates:
    end = isoparse(period['period_end']).date()
    if end < one_day:
        continue

    if end > one_day:
        break

    #  assumes 30 minute intervals - should check
    pv_estimate =  pv_estimate + (period['pv_estimate'] / 2)
    pv_estimate10 =  pv_estimate10 + (period['pv_estimate10'] / 2)
    pv_estimate90 =  pv_estimate90 + (period['pv_estimate90'] / 2)

print("PV total =", pv_estimate)
print("PV 10 total =", pv_estimate10)
print("PV 90 total =", pv_estimate90)
print("End:", end)

# historic data ...
#result_actuals = get_solcast_estimated_actuals(SOLCAST_APIKEY, SOLCAST_SYSID)
#print(result_actuals)

