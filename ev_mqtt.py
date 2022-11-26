#!/usr/bin/env python3

# ev_mqtt.py

import paho.mqtt.client as mqtt
import time
import sys
sys.path.insert(0, '/home/pi/ME3000')
from MyKeys import *


# topics for house load
HB_W = 'highbanks/load'
HB_V = 'highbanks/voltage'

# topics and values for openevse
EV_A = 'highbanks/ev_amp'
QOS = 2


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK Returned code =", rc)

        ret = client.subscribe([(HB_W, 2),(HB_V, 2),(EV_A, 2)])
        if ret[0] != 0:
            print("Subscribe failed")


def on_message(client, userdata, message):
    mesg = message.payload.decode()
    print(mesg)


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+ str(mid) + " " + str(granted_qos))


def on_publish(client, userdata, mid):
    sub_id = mid
    print("Publish OK");


def load_callback(client, userdata, message):
    global house_load
    house_load = float(message.payload.decode())
    print("Highbanks load =", house_load)
    do_control()


def voltage_callback(client, userdata, message):
    global house_voltage
    house_voltage = float(message.payload.decode())
    print("Highbanks voltage =", house_voltage)


def evamp_callback(client, userdata, message):
    global ev_amps
    ev_amps = message.payload.decode()
    print("EV current =", ev_amps)


def do_control():
    global house_voltage
    global house_load
    global ev_amps
    global ev_setcharge

    print("do_control:  house_voltage = ",  house_voltage, ", house_load= ", house_load, ", ev_amps = ", ev_amps, "max charge = ", ev_setcharge)

    if house_load >= HB_MAXLOAD:
        # we need to see if we can reduce the load
        delta_w =  house_load - HB_MAXLOAD
        delta_a = delta_w / house_voltage

        if ev_amps > 0:
            # we are charging ...
            if ev_setcharge > delta_a:
                ev_setcharge -= delta_a
                if ev_setcharge < HB_MINCHARGE:
                     ev_setcharge = 0
            else:
                # current set charge is already less than needed
                ev_setcharge = 0
            do_evsetcharge()

        ret = client.publish(RELAY1, R_OFF, QOS)
    
        if ts2_temp < TS2_MAXTEMP:
            ret = client.publish(RELAY2, R_ON, QOS)
        else:
            ret = client.publish(RELAY2, R_OFF, QOS)
    else:
        # do we need to increase the EV max charge?
        if house_load >= 0 and ev_setcharge < HB_MAXCHARGE:
            delta_w = HB_MAXLOAD - house_load
            delta_a = delta_w / house_voltage
            ev_setcharge = min(delta_a, HB_MAXCHARGE)

        
        ret = client.publish(RELAY2, R_OFF, QOS)
        ret = client.publish(RELAY1, R_ON, QOS)


# main code ...
client = mqtt.Client(EV_NAME)

# callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.on_publish = on_publish

# initial values
house_load = 0
house_voltage = 0
ev_amps = 0
ev_setcharge = 32

client.connect(MQTT_HOST)
client.message_callback_add(HB_W, load_callback)
client.message_callback_add(HB_V, voltage_callback)
client.message_callback_add(EV_A, evamp_callback)

client.loop_forever()
client.disconnect()
