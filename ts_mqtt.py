#!/usr/bin/env python3

# ts_mqtt.py

import paho.mqtt.client as mqtt
import time
import sys
sys.path.insert(0, '/home/pi/ME3000')
from MyKeys import *


# topic for thermostats on the thermal stores
TS_1 = 'thermal_store/ts1'
TS_2 = 'thermal_store/ts2'

# topics and values for relay control
RELAY1 = 'emon/immersion/thermal_store'
RELAY2 = 'emon/immersion/buffer_store'
R_ON = '1'
R_OFF = '0'
QOS = 2


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK Returned code =", rc)

        ret = client.subscribe([(TS_1, 2),(TS_2, 2),(RELAY1, 2),(RELAY2, 2)])
        if ret[0] != 0:
            print("Subscribe failed")

        # ensure both thermostats are initially off ...
        ret = client.publish(RELAY1, R_OFF, QOS)
        ret = client.publish(RELAY2, R_OFF, QOS)


def on_message(client, userdata, message):
    mesg = message.payload.decode()
    print(mesg)


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+ str(mid) + " " + str(granted_qos))


def on_publish(client, userdata, mid):
    sub_id = mid
    #print("Publish OK");


def ts1_callback(client, userdata, message):
    global ts1_temp
    ts1_temp = float(message.payload.decode())
    #print("TS1 temp =", ts1_temp)
    do_control()


def ts2_callback(client, userdata, message):
    global ts2_temp
    ts2_temp = float(message.payload.decode())
    #print("TS2 temp =", ts2_temp)
    do_control()


def relay1_callback(client, userdata, message):
    global r1_stat
    r1_stat = message.payload.decode()
    #print("Relay1 status =", r1_stat)


def relay2_callback(client, userdata, message):
    global r2_stat
    r2_stat = message.payload.decode()
    #print("Relay2 status =", r2_stat)


def do_control():
    global ts1_temp
    global ts2_temp
    #print("do_control: ts1 temp = ", ts1_temp, "ts2 temp = ", ts2_temp)
    if ts1_temp >= TS1_MAXTEMP:
        # ensure R1 is off ...
        ret = client.publish(RELAY1, R_OFF, QOS)
    
        if ts2_temp < TS2_MAXTEMP:
            ret = client.publish(RELAY2, R_ON, QOS)
        else:
            ret = client.publish(RELAY2, R_OFF, QOS)
    else:
        # ts1 < threshold
        # ensure R2 off ...
        ret = client.publish(RELAY2, R_OFF, QOS)
        ret = client.publish(RELAY1, R_ON, QOS)


# main code ...
client = mqtt.Client(TS_NAME)

# callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.on_publish = on_publish

# initial control temperatures
ts1_temp = 0
ts2_temp = 0
r1_stat = None
r2_stat = None

client.connect(MQTT_HOST)
client.message_callback_add(TS_1, ts1_callback)
client.message_callback_add(TS_2, ts2_callback)
client.message_callback_add(RELAY1, relay1_callback)
client.message_callback_add(RELAY2, relay2_callback)

client.loop_forever()
client.disconnect()
