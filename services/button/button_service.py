'''
Single Click types    
    short
    medium 
    long 

Multiple clicks Types
    short_multi 
    short_medium 
    short_long 
'''

import RPi.GPIO as GPIO
import json 
import time
import signal
import threading
import sys
import os

# GoodWand Libraries
sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
#from MQTTObject import MQTTObject
from log import log
from Services import LightService
from Services import AudioService
from Services import MQTTClient
from tgw_timer import tgw_timer as Button_Timer

DEBUG_LEVEL = "INFO"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)


BATTERY_SERVICE_PATH = "../battery_charger"

MQTT_TYPE = "UI_BUTTON"
MQTT_VERSION = "1"


BUTTON_PIN = 26
BUTTON_TOPIC = "goodwand/ui/controller/button"
BUTTON_CLIENTID = 'TGW-ButtonService'

SHORT_PRESS_TIMER = 0.20
MEDIUM_PRESS_DURATION = 1.5
LONG_PRESS_DURATION = 5.0

# Single click IDS
SHORT_ID = 'short'
MEDIUM_ID = 'medium'
LONG_ID = 'long'

# Multi click IDS
SHORT_MULTI_ID = 'short_multi'
SHORT_MEDIUM_ID = 'short_medium'

        
class TGWButtonService():
    """
    Handles button info!
    """
    def __init__(self) -> None:
        self.mqtt_client = None
        self.click_count = 0
        self.short_timer = Button_Timer(SHORT_PRESS_TIMER, self.short_press_callback, name ="short timer") # Used for multi click 
        self.medium_timer = Button_Timer(MEDIUM_PRESS_DURATION, self.medium_press_callback, name="medium timer")
        self.long_timer = Button_Timer(LONG_PRESS_DURATION, self.long_press_callback, name="long timer")
        self.press_id = SHORT_ID


    def gpio_init(self):
        """RPi.GPIO config"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


    def publish_button_press(self, id):     
        logger.debug(f"Publish press id:{id} count:{self.click_count}")
        header = {"type": MQTT_TYPE, "version": MQTT_VERSION}
        data = {"event": id, "count": self.click_count}
        msg = {"header": header, "data": data}
        self.click_count = 0
        self.mqtt_client.publish(BUTTON_TOPIC, json.dumps(msg))
      

    def short_press_callback(self):
        if self.click_count > 1:
            self.press_id = SHORT_MULTI_ID
        else:
            self.press_id = SHORT_ID

        self.publish_button_press(self.press_id)
        logger.debug(f"Short timer expired id:{self.press_id} count:{self.click_count}")
        

    def medium_press_callback(self):
        # Has the button been click before the short timer expiry?
        if self.click_count > 1: 
            self.press_id = SHORT_MEDIUM_ID
        else:
            self.press_id = MEDIUM_ID
        logger.debug(f"Medium Press expired. ID: {self.press_id}")
        self.publish_button_press(self.press_id)


    def long_press_callback(self):
        # Has the button been click before the short timer expiry?

        self.press_id = LONG_ID

        self.publish_button_press(self.press_id)
        logger.debug(F"Long timer expired. ID {self.press_id}")
        logger.info("Powering down")
        self.lights.lb_csv_animation("power_off.csv")
        self.audio.play_background("power_off.wav")
        time.sleep(4)
        os.system("sudo python3 " + os.path.expanduser(BATTERY_SERVICE_PATH) +'/charger_cli.py --power_off')


    def trigger_event_down(self):
        """Start timers """
        self.click_count += 1
        logger.debug(f"Click Count {self.click_count}")
        self.press_id = SHORT_ID
        self.short_timer.stop()
        self.medium_timer.start()
        self.long_timer.start()


    def trigger_event_up(self):
        """
        Stops timers for medium and long presses
        Start short press timer
        All publishing happens in the timer callbacks when one expires. 
        """
        self.medium_timer.stop()
        self.long_timer.stop()
        
        if self.press_id == SHORT_ID:
            self.short_timer.start() 
            
        logger.info(f"Button Released: {self.press_id} press detected")
        


    def trigger(self, *args):
        """flow of logic for interrupt callback"""

        if GPIO.input(BUTTON_PIN):
            self.trigger_event_up()
        else:
            self.trigger_event_down()

    def run(self):
        """main loop"""
        
        self.mqtt_object = MQTTClient()
        self.mqtt_client = self.mqtt_object.start(BUTTON_CLIENTID)
        self.lights = LightService(self.mqtt_client, path = os.getcwd())
        self.audio = AudioService(mqtt_client = self.mqtt_client, path = os.getcwd())

        self.gpio_init()
        GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=self.trigger)

        signal.pause()

if __name__ == '__main__':
    try:
        service = TGWButtonService()
        service.run()
    finally:
        GPIO.cleanup()