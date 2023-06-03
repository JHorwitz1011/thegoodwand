import threading
import RPi.GPIO as GPIO
from bq24296M import bq24296M
import signal
import sys, os
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


# System status strings

VBUS_STATUS_STR = ["Unknown", "USB Host", "Adapter Port", "OTG"]
CHRG_STATUS_STR = ["Not Charging", "Pre Charge", "Fast Charging", "Charge Done"]
DPM_STATUS_STR = ["Not DPM", "In dynamic power management. Source Overloaded"]
PG_STATUS_STR = ["Not Good Power", "Power Good"]
THERM_STATUS_STR = ["Normal", "In Thermal Regulation"]
VSYS_STATUS_STR = ["Not in VSYSMIN regulation (BAT > VSYSMIN)", "In VSYSMIN regulation (BAT < VSYSMIN)"]



WATCHDOG_FAULT = ["Normal", "Watchdog timer expired"]
OTG_FAULT = ["Normal", "VBUS overloaded in OTG, or VBUS OVP, or battery is too low"]
CHRG_FAULT = ["Normal", "Input fault","Thermal Shutdown", "Charge timer expired"]
BAT_FAULT = ["Normal", "Battery OVP"]
NTC_FAULT = ["Normal", "Hot", "Cold", "hot cold"]


MQTT_CLIENT_ID = "charger_services"

def charger_init():
    #set 500mA charge current limit
    charger.setICHG(charger.ICHRG_512MA)
    
    #disable I2C Watchdog.
    charger.setWatchdog(charger.WATCHDOG_DISABLE)


def button_callback(press):
    logger.debug(f"button callback {press} ")

def print_faults(faults):
    logger.debug(f"Charger {faults}")



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
        status = charger.getSystemStatus()
        logger.debug(f"Charge status {CHRG_STATUS_STR[(status & charger.CHRG_STAT_MASK) >> charger.CHRG_STAT_SHIFT]}")
        if faults :
            print_faults(faults)
        

        time.sleep(60) 


