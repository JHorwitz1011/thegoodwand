# python 3.6

import json
import RPi.GPIO as GPIO
import sys
import os
import signal
import time

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from MQTTObject import MQTTObject
from log import log

DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)

port = 1883
UV_TOPIC = "goodwand/ui/view/uv"

UV_CLIENT_ID = 'TGW_UVService'

UV_PIN = 27


class FWUVService(MQTTObject):
    #set constants and the such
    def __init__(self):
        super().__init__()
        self.pinStatus = False
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(UV_PIN, GPIO.OUT)
        GPIO.output(UV_PIN, 0)
        self.callbacks = {
            UV_TOPIC : self.on_uv_message
         }

    def update_uv(self, pinStatus):
        if pinStatus is not None:
            self.pinStatus = pinStatus
        logger.info(f"Setting UVLED value to {pinStatus}")
        GPIO.output(UV_PIN, pinStatus) 

    def on_uv_message(self, client, userdata, msg):
        payload = json.loads(msg.payload)
        logger.debug(payload)
        try:
            timeOn = payload["data"].get("timeOn")
            GPIO.output(UV_PIN, 1) 
            time.sleep (timeOn)
            GPIO.output(UV_PIN, 0) 
            

        except KeyError:
            logger.debug(f"UV ERROR parsing incoming message")

    ################## MAIN LOOP ##########################
    def run(self):
        logger.debug ("UV Running self")
        self.start_mqtt(UV_CLIENT_ID, self.callbacks)
        signal.pause()



    ################# LIGHT HANDLING ######################

        

if __name__ == '__main__':
    service = FWUVService()  
    service.run()