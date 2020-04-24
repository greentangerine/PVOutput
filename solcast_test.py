#!/usr/bin/env python3

# solcast_test.py

# read forecast etc.

import sys
sys.path.insert(0, '/home/pi/PVOutput')

# API keys etc.
from MyKeys import *
from solcast import get_solcast_forecast, get_solcast_estimated_actuals

result = get_solcast_forecast(SOLCAST_APIKEY, SOLCAST_SYSID)

print(result)

result = get_solcast_estimated_actuals(SOLCAST_APIKEY, SOLCAST_SYSID)

print(result)
