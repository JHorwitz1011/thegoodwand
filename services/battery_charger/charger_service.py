import threading
import RPi.GPIO as GPIO
from bq24296M import bq24296M
import signal
import sys
import time

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))

from Services import MQTTClient
from Services import ButtonService
from Services import LightService
from Services import IMUService
from log import log

DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)


MQTT_CLIENT_ID = "charger_services"

def charger_init():
    #set 500mA charge current limit
    charger.setICHG(charger.ICHRG_512MA)
    
    #disable I2C Watchdog.
    charger.setWatchdog(charger.WATCHDOG_DISABLE)


def button_callback(press):
    logger.debug(f"button callback {press} ")


def signal_handler(sig, frame):
    logger.info(f"Terminating charger service {sig} ")
    GPIO.cleanup()
    sys.exit(0)

if __name__ == "__main__":

    logger.info("Charger service started")

    charger = bq24296M()
    
    mqtt_object = MQTTClient()
    mqtt_client = mqtt_object.start(MQTT_CLIENT_ID)

    button = ButtonService(mqtt_client)
    button.subscribe(button_callback)

    charger_init()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while(1):

        faults = charger.getNewFaults()
        logger.debug(f"faults {faults}")        
        time.sleep(60) 


