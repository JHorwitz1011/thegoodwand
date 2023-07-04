import RPi.GPIO as GPIO
from bq24296M import bq24296M
import signal
import sys, os
import time
import json


sys.path.append(os.path.expanduser('~/thegoodwand/templates'))

from Services import MQTTClient
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

MQTT_TYPE = "CHARGER"
MQTT_VERSION = "1"
MQTT_CLIENT_ID = "charger_services"
STATUS_TOPIC = "goodwand/battery/status"
FAULTS_TOPIC = "goodwand/battery/faults"


def charger_init():
    #set 500mA charge current limit
    charger.setICHG(charger.ICHRG_512MA)
    
    #disable I2C Watchdog.
    charger.setWatchdog(charger.WATCHDOG_DISABLE)


def publish_faults(client, faults):
    header = {"type": MQTT_TYPE, "version": MQTT_VERSION}
    data = {"faults": faults}
    msg = {"header": header, "data": data}
    client.publish(FAULTS_TOPIC, json.dumps(msg))

def publish_status(client, status):
    header = {"type": MQTT_TYPE, "version": MQTT_VERSION}
    data = {"status": status}
    msg = {"header": header, "data": data}
    client.publish(STATUS_TOPIC, json.dumps(msg))


def signal_handler(sig, frame):
    logger.info(f"Terminating charger service {sig} ")
    GPIO.cleanup()
    sys.exit(0)

if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Charger service started")
    charger = bq24296M()
    mqtt_object = MQTTClient()
    mqtt_client = mqtt_object.start(MQTT_CLIENT_ID)
    last_faults = 0
    last_status = 0
    temperature_mask = 0x03
    charger_mask = 0x30

    charger_init()

    while(1):

        faults = charger.getNewFaults() & temperature_mask
        status = charger.getSystemStatus() & charger_mask
        logger.debug(f"Charge status {status}={CHRG_STATUS_STR[(status & charger.CHRG_STAT_MASK) >> charger.CHRG_STAT_SHIFT]}")
        
        if status != last_status:
            logger.debug(f"Status Changed {status}")
            publish_status(mqtt_client, status)
            last_status = status

        if faults != last_faults :
            logger.debug(f"Faults Changed {faults}")
            publish_faults(mqtt_client, faults)
            last_faults = faults
        
        time.sleep(20) 