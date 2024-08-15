import sys, os, time, signal, math
import random
import pyttsx3

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from Services import MQTTClient
from Services import ButtonService
from Services import LightService
from Services import AudioService
from Services import IMUService
from Services import GestureRecService
from log import log

DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)

MQTT_CLIENT_ID = "COLOS_SPELL"

NORMALIZE = float(255/90)

gesture_completed = False
target_gesture = None

def magnitude(vector):
    return math.sqrt(sum(pow(element, 2) for element in vector))

# Receives "short", "medium", "long"
def button_callback(press):
    # User Code Here
    logger.debug(f"Recieved Press {press}")
    
    if press == "short":
        pass
        

def gesture_callback(param):
    global gesture_completed
    if not gesture_completed:
        if param == target_gesture:
            gesture_completed = True
            success()

# Initialize button. return button object
def init_button(mqtt_client, callback):
    button = ButtonService(mqtt_client)
    button.subscribe(button_callback)
    return button 

def init_lights(mqtt_client, path): 
    return LightService(mqtt_client = mqtt_client, path = path)

def init_audio(mqtt_client, path):
    return AudioService(mqtt_client = mqtt_client, path = path)

def init_gesturerec(mqtt_client, path):
    gesture = GestureRecService(mqtt_client = mqtt_client)
    gesture.subscribe(gesture_callback)
    return gesture

# Cleanup
def signal_handler(sig, frame): 
    # Turn off raw data stream
    imu.disable_stream()
    logger.debug("disable stream")
    lights.lb_clear()
    time.sleep(.1)
    
    #GPIO.cleanup()
    sys.exit(0)

 
if __name__ == '__main__':
    # Initialize the TTS engine
    speaker = pyttsx3.init()
    # Set properties (optional)
    speaker.setProperty('rate', 150)  # Speed of speech (words per minute)
    speaker.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
    speaker.say('this is a test')
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
    gesture = init_gesturerec(mqtt_client, spellPath)
   
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    
    signal.pause()

