#!/usr/bin/env python3

# weatherbit_test.py

# read forecast etc.

import sys
sys.path.insert(0, '/home/pi/PVOutput')

# API keys etc.
from MyKeys import *
from weatherbit import *

DAYS=1

result = get_weatherbit_forecast(WEATHERBIT_APIKEY, LAT, LONG, DAYS)

print(result)

result = get_weatherbit_current(WEATHERBIT_APIKEY, LAT, LONG)

print(result)
