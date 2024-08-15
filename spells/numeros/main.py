import sys, os, time, signal, math
import random
import json
import pyttsx3

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from Services import MQTTClient
from Services import ButtonService
from Services import LightService
from Services import AudioService
from Services import GestureRecService
from Services import NFCService
from log import log

DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)

MQTT_CLIENT_ID = "NUMEROS_SPELL"

# Initialize the TTS engine
speaker = pyttsx3.init()
# Set properties (optional)
speaker.setProperty('rate', 125)  # Speed of speech (words per minute)
speaker.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)

count = 0
current_string = ""
most_recent_number = ""

def success():
    global count, current_string

    lights.lb_system_animation("confused_not_understood")
    time.sleep(1)
    count += 1
    speaker.say(str(int(current_string)) + " is correct!")
    speaker.runAndWait()

    current_string = "0"

def failure():
    global count, current_string

    lights.lb_system_animation("no_failed")
    time.sleep(1)
    speaker.say(str(int(current_string)) + " is incorrect. Back to the beginning! Start with 1.")
    count = 0
    speaker.runAndWait()

    current_string = "0"

# Receives "short", "medium", "long"
def button_callback(press):
    global next_number, current_string, most_recent_number
    time.sleep(.5)

    logger.debug(f"Recieved Press {press}")    
    if press == "short":
        current_string += most_recent_number
        if int(current_string) > count + 1:
                failure()
        elif int(current_string) == count + 1:
                success()

def nfc_callback(param):
    global next_number, current_string, most_recent_number

    audio.play_background('on_scan.wav')
    lights.lb_system_animation("select")
    logger.debug(f"Recieved nfc {param}")    
    most_recent_number = json.loads(param['card_data']['records'][1]["data"])["data"]
    


# Initialize button. return button object
def init_button(mqtt_client, callback):
    button = ButtonService(mqtt_client)
    button.subscribe(button_callback)
    return button 

def init_lights(mqtt_client, path): 
    return LightService(mqtt_client = mqtt_client, path = path)

def init_audio(mqtt_client, path):
    return AudioService(mqtt_client = mqtt_client, path = path)

def init_nfc(mqtt_client, path):
    nfc = NFCService(mqtt_client)
    nfc.subscribe(nfc_callback)
    print("init nfc called")
    return nfc

# Cleanup
def signal_handler(sig, frame): 
    # Turn off raw data stream
    logger.debug("disable stream")
    lights.lb_clear()
    time.sleep(.1)
    
    #GPIO.cleanup()
    sys.exit(0)

 
if __name__ == '__main__':

    speaker.say('Lets count!')
    speaker.runAndWait()
    # Connect to MQTT and get client instance 
    logger.debug("Starting Mirror spell")
    mqtt_object = MQTTClient()
    mqtt_client = mqtt_object.start(MQTT_CLIENT_ID)

    # Get out path
    param_1 = sys.argv[1]
    param_2 = sys.argv[2] 
	    
    # if started by conductor, param1 is the path,
	# otherwise use cwd
    
    if param_1 !="":
        spellPath = param_1
    else:
        spellPath = os.getcwd() 

    audio   = init_audio(mqtt_client, spellPath)
    button  = init_button(mqtt_client, button_callback)
    lights  = init_lights(mqtt_client, spellPath)
    nfc     = init_nfc(mqtt_client, spellPath)
   
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    signal.pause()

