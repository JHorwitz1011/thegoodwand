import time
import signal
import json
from multiprocessing import Process
import subprocess
import logging

import sys
import os
sys.path.append(os.path.expanduser('~/thegoodwand/templates'))

#from MQTTObject import MQTTObject
from Services import *
from log import log

def init_audio(mqtt_client, path):
    return AudioService(mqtt_client = mqtt_client, path = path)


if __name__ == '__main__':
    mqttobj = MQTTClient()
    mqttclient = mqttobj.start("lumos")

    param_1 = ""
    param_2 = ""
    if len(sys.argv) > 1 :
        param_1= sys.argv[1] 
    
    if len(sys.argv) > 2 :
        param_2= sys.argv[2] 


    if param_1 !="":
        spellPath = param_1
    else:   
        spellPath =os.getcwd() 
    
    audio   = init_audio(mqttclient, spellPath)
    audio.play_background("lumos1.wav")

    lights = LightService(mqttclient)
    lights.lb_fire(0xaa, 0x42, 0x03)
    # lights.bl_heartbeat(0xaa, 0x42, 0x03)
    
    signal.pause()