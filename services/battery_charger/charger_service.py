import threading
import RPi.GPIO as GPIO
from bq24296M import bq24296M
import signal
import sys, os
import time
import configparser
import subprocess

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))

from Services import MQTTClient
from Services import ButtonService
from Services import LightService
from Services import IMUService
from log import log
from tgw_timer import tgw_timer

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

INACTIVITY_TIME = 10

class PowerManagement():

    SYSTEM_READY = 2
    SYSTEM_IDLE = 1
    SYSTEM_PD = 0

    def __init__(self, charger) -> None:
        
        self.system_state = self.SYSTEM_READY
        self.charger = charger

    def idle(self):
        if self.is_usb_power:
            logger.debug("System State Idle > Running")
            self.system_state = self.SYSTEM_IDLE
            self.__disable_wifi()
            self.__disable_service()

        else: 
            logger.debug("unplugged, power down")
            self.system_state = self.SYSTEM_IDLE
            self.__power_down()
            
    def run(self):
        logger.debug("System State Idle > Running")
        self.__enable_wifi()
        self.__enable_service()
        # TODO Power up services.
        pass

    def __power_down(self):

        logger.debug("Power down system")
        
    def is_usb_power(self) -> bool:     
        return True if self.charger.getVbusStatus() else False
    
    def __enable_wifi(self):
        logger.debug("Turning on wifi")
        #subprocess.run(["sudo", "ifconfig", "wlan0", "up"])
        
    def __disable_wifi(self):
        logger.debug("Turning off wifi")
        #subprocess.run(["sudo", "ifconfig", "wlan0", "down"])

    def __disable_service(self):
        logger.debug("Turning off TGW services")

    def __enable_service(self):
        logger.debug("Turning on TGW services")


            

def charger_init():
    #set 500mA charge current limit
    charger.setICHG(charger.ICHRG_512MA)
    
    #disable I2C Watchdog.
    charger.setWatchdog(charger.WATCHDOG_DISABLE)


def print_faults(faults):
    logger.debug(f"Charger faults {faults}")


def inactivity_timer_cb():
    logger.debug("Inactivity expired")
    power_management.idle()

def button_callback(press):
    
    logger.debug(f"button callback {press} ")

    if press == "long":
        power_management.idle()
    
    elif power_management.system_state == power_management.SYSTEM_IDLE:
        power_management.run()
    
def imu_on_wake_callback(wake_status:'bool'):
    '''
        Start the inactivity timer if idle
        stop Inactiviy time if not expired on wake 
        Do nothing if system is idle. Button press needed to wake.
    '''
    if wake_status == True: 
        logger.debug(f"Wand is active {wake_status}")
        inactivity_timer.stop()
    elif wake_status == False: 
        logger.debug(f"Wand is inactive {wake_status}")
        inactivity_timer.start()
    else:    
        logger.debug(f"Unknown active state {wake_status}")
        inactivity_timer.stop()

def signal_handler(sig, frame):
    logger.info(f"Terminating charger service {sig} ")
    GPIO.cleanup()
    sys.exit(0)

if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Charger service started")
    charger = bq24296M()
    power_management = PowerManagement(charger)
    mqtt_object = MQTTClient()
    mqtt_client = mqtt_object.start(MQTT_CLIENT_ID)
    button = ButtonService(mqtt_client)
    button.subscribe(button_callback)
    imu = IMUService(mqtt_client)
    imu.subscribe_on_wake(imu_on_wake_callback)
    inactivity_timer = tgw_timer(60, inactivity_timer_cb, name = "inactivity")

    charger_init()

    while(1):

        faults = charger.getNewFaults()
        status = charger.getSystemStatus()
        logger.debug(f"Charge status {CHRG_STATUS_STR[(status & charger.CHRG_STAT_MASK) >> charger.CHRG_STAT_SHIFT]}")
        if faults :
            print_faults(faults)
        
        time.sleep(60) 


