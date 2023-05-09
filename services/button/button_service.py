



import RPi.GPIO as GPIO
import json 
import time
import signal

import sys
import os
sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from MQTTObject import MQTTObject

BATTERY_SERVICE_PATH = "../battery_charger"

pkt_template = {
    "header": {
        "type": "UI_BUTTON",
        "version": 1
    },
    "data": {
        "event": None,
    }
}

BUTTON_PIN = 26
BUTTON_TOPIC = "goodwand/ui/controller/button"
BUTTON_CLIENTID = 'TGW-ButtonService'
LONG_PRESS_DURATION = 1
SHUTDOWN_LENGTH = 5
SHORT_PRESS_ID = 'short'
LONG_PRESS_ID = 'long'

class TGWButtonService(MQTTObject):
    """
    Handles button info!
    """
    def __init__(self) -> None:
        super().__init__()

        self.client = None
        self.press_start = 0
        self.press_end = 0

    def gpio_init(self):
        """RPi.GPIO config"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def trigger_event_down(self):
        """registers time on down edge of button press"""
        self.press_start = time.time()

    def trigger_event_up(self):
        """calculates duration on up edge of button press - handles correspond event accordingly"""
        self.press_end = time.time()
        duration = self.press_end - self.press_start

        if duration > SHUTDOWN_LENGTH:                              # power off
            os.system("sudo python3 " + os.path.expanduser(BATTERY_SERVICE_PATH) +'/charger_cli.py --power_off')
        else:
            pkt = pkt_template
            if duration < LONG_PRESS_DURATION:                      # trigger short
                pkt['data']['event'] = SHORT_PRESS_ID 
            else:                                                   # trigger long
                pkt['data']['event'] = LONG_PRESS_ID        

            print(f"publishing {pkt['data']['event']} press")
            self.publish(BUTTON_TOPIC, json.dumps(pkt))


    def trigger(self, *args):
        """flow of logic for interrupt callback"""

        if GPIO.input(BUTTON_PIN):
            self.trigger_event_up()
        else:
            self.trigger_event_down()

    def run(self):
        """main loop"""
        self.gpio_init()
        self.start_mqtt(BUTTON_CLIENTID)
        GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=self.trigger)
        signal.pause()

if __name__ == '__main__':
    try:
        service = TGWButtonService()
        service.run()
    finally:
        GPIO.cleanup()