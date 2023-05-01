import threading
import RPi.GPIO as GPIO
from bq24296M import bq24296M
import signal
import sys


POWER_DOWN_TIMEOUT = 5
BUTTON = 26

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def power_down():
    
    bn_release_event.wait(POWER_DOWN_TIMEOUT)

    #Regular button press, do nothing
    if bn_release_event.is_set():
        bn_release_event.clear()
    
    #long button press, power down.
    else: 
        charger.powerDown()

#Interrupt Handler for button GPIO 26
def button_callback(channel):
    
    if not GPIO.input(channel): 
        print("Button Pressed")
        t1 = threading.Thread(target=power_down)
        t1.start()
    else:
        bn_release_event.set()
        print("Released")


def charger_init():
    
    #set 500mA charge current limit
    charger.setICHG(charger.ICHRG_512MA)
    
    #disable I2C Watchdog.
    charger.setWatchdog(charger.WATCHDOG_DISABLE)


GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down = GPIO.PUD_UP)


GPIO.add_event_detect(BUTTON, GPIO.BOTH, callback = button_callback, bouncetime = 10)

bn_release_event = threading.Event()
charger = bq24296M()
charger_init()


signal.signal(signal.SIGINT, signal_handler)
signal.pause()