#!/usr/bin/env python3

# openweathermap_test.py

# read forecast etc.

import sys
sys.path.insert(0, '/home/pi/PVOutput')

# API keys etc.
from MyKeys import *
from openweathermap import *

DAYS=1

result = get_openweathermap_data(OPENWEATHERMAP_APIKEY, LAT, LONG)

print(result)
