#!/usr/bin/env python3

# ts_mqtt.py

import paho.mqtt.client as mqtt
import time
import sys
sys.path.insert(0, '/home/pi/ME3000')
from MyKeys import *

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True 
        print("connected OK Returned code=", rc)
        client.subscribe(TS1)
        client.subscribe(TS2)
    else:
        print("Bad connection Returned code= ", rc)
        client.bad_connection_flag = True

mqtt.Client.bad_connection_flag = False
mqtt.Client.connected_flag = False

client = mqtt.Client(TS_NAME)
client.on_connect = on_connect
client.loop_start()
client.connect(MQTT_HOST)

while not client.connected_flag and not client.bad_connection_flag:
    time.sleep(1)

if client.bad_connection_flag:
    client.loop_stop()
    print("MQTT connection failed ...")
    quit()

# topic for thermostats on the thermal stores
TS_1 = 'emon/emonth6/external temperature'
TS_2 = 'emon/emonth7/external temperature'

# topics and values for relay control
RELAY1 = 'immersion/thermal_store'
RELAY2 = 'immersion/buffer_store'
R_ON = '1'
R_OFF = '0'

ret = client.publish(RELAY1, R_ON)
if ret[0] != 0:
    print("Publish failed for" + RELAY1)

client.disconnect()
