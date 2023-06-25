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


if __name__ == '__main__':
    mqttobj = MQTTClient()
    mqttclient = mqttobj.start("lumos")

    lights = LightService(mqttclient)
    lights.lb_fire(0xaa, 0x42, 0x03)
    lights.bl_heartbeat(0xaa, 0x42, 0x03)
    signal.pause()