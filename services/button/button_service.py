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

DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)


BATTERY_SERVICE_PATH = "../battery_charger"

MQTT_TYPE = "UI_BUTTON"
MQTT_VERSION = "1"


BUTTON_PIN = 26
BUTTON_TOPIC = "goodwand/ui/controller/button"
BUTTON_CLIENTID = 'TGW-ButtonService'

MEDIUM_PRESS_DURATION = 1.5
LONG_PRESS_DURATION = 5.0

SHORT_PRESS_ID = 'short'
MEDIUM_PRESS_ID = 'medium'
LONG_PRESS_ID = 'long'

class Button_timer():

    def __init__(self, interval, function, args=[], kwargs={}, name=""):
        self._interval = interval
        self._function = function
        self._args = args
        self._kwargs = kwargs
        self.timer = None
        self.timer_name = name
        self.lights = None
        self.audio = None

    def start_timer(self):
        self.timer = threading.Timer(self._interval, self._function, self._args, self._kwargs)
        self.timer.setName(self.timer_name)
        self.timer.start()
        pass

    def cancel_timer(self):
        try:
            logger.debug(f"Timer Canceled {self.timer.getName()}")
            self.timer.cancel()
        except Exception as e:
            logger.warning(f"cancel timer error {e}")
 

    def is_alive(self):
        try: 
            if self.timer.is_alive():
                return True
            else:
                return False
        except Exception as e:
            logger.warning(f"is alive exception {e}")
            return False 
        
class TGWButtonService():
    """
    Handles button info!
    """
    def __init__(self) -> None:
        self.mqtt_client = None
        self.medium_timer = Button_timer(MEDIUM_PRESS_DURATION, self.medium_press_callback, name="medium timer")
        self.long_timer = Button_timer(LONG_PRESS_DURATION, self.long_press_callback, name="long timer")
        self.press = SHORT_PRESS_ID
        self.press_mutex = threading.Lock()

    def gpio_init(self):
        """RPi.GPIO config"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def publish_button_press(self, id):     
        header = {"type": MQTT_TYPE, "version": MQTT_VERSION}
        data = {"event": id}
        msg = {"header": header, "data": data}
        self.mqtt_client.publish(BUTTON_TOPIC, json.dumps(msg))

    # Called if the timer defined by MEDIUM_PRESS_DURATION expires 
    def medium_press_callback(self):
        logger.debug("Medium Press timer expired")
        self.press_mutex.acquire()
        self.press = MEDIUM_PRESS_ID
        self.press_mutex.release()
        self.publish_button_press(self.press)

    # Called if the timer defined by LONG_PRESS_DURATION expires 
    def long_press_callback(self):
        self.press_mutex.acquire()
        self.press = LONG_PRESS_ID
        self.press_mutex.release()
        self.publish_button_press(self.press)
        logger.debug("Long Press timer expired")
        logger.info("Powering down")
        self.lights.play_lb_csv_animation("power_off.csv")
        self.audio.play_foreground("power_off.wav")
        time.sleep(3)
        #TODO Play power down animation
        os.system("sudo python3 " + os.path.expanduser(BATTERY_SERVICE_PATH) +'/charger_cli.py --power_off')


    def trigger_event_down(self):
        """Start timers """
        #Reset press state
        self.press_mutex.acquire()
        self.press = SHORT_PRESS_ID
        self.press_mutex.release()
        self.medium_timer.start_timer()
        self.long_timer.start_timer()


    def trigger_event_up(self):
        """Stops timers for medium and long presses"""
        self.medium_timer.cancel_timer()
        self.long_timer.cancel_timer()
        logger.info(f"Button Released: {self.press} press detected")
        
        ## Medium and long presses handled in the timer callbacks. Only publish short press
        if self.press == SHORT_PRESS_ID:
            self.publish_button_press(SHORT_PRESS_ID) 


    def trigger(self, *args):
        """flow of logic for interrupt callback"""

        if GPIO.input(BUTTON_PIN):
            self.trigger_event_up()
        else:
            self.trigger_event_down()

    def run(self):
        """main loop"""
        
        self.mqtt_object = MQTTClient()
        self.mqtt_client = self.mqtt_object.start_mqtt(BUTTON_CLIENTID)
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