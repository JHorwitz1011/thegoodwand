""" Unit tests for Service Files """
import sys, os, time, signal, math
import random

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

gesture_completed = None
target_gesture = None

def magnitude(vector):
    return math.sqrt(sum(pow(element, 2) for element in vector))

# Receives "short", "medium", "long"
def button_callback(press):
    # User Code Here
    logger.debug(f"Recieved Press {press}")
    
    if press == "short":
        pass
        
def orientation_callback(orientation):
    logger.debug(f"IMU orientation {orientation}")

def get_vector(data) -> "vector[3]":
    return [data['x'], data['y'], data['z']]

def tilt_angle(vector,  mag):
    x = int(math.degrees(math.asin(vector[0]/mag)))
    y= int(math.degrees(math.asin(vector[1]/mag)))
    z = int(math.degrees(math.asin(vector[2]/mag)))
    return  x, y, z


def display_lights(x,y,z):
    x_buffer.append(abs(x*NORMALIZE))
    y_buffer.append(abs(y*NORMALIZE))
    z_buffer.append(abs(z*NORMALIZE))
    red = int(sum(x_buffer) / buffer_size)
    green = int(sum(y_buffer) / buffer_size)
    blue = int(sum(z_buffer) / buffer_size)
    lights.lb_block(red, green, blue)
    logger.debug(f"r: {red} g: {green}  b: {blue}  {z*NORMALIZE} {NORMALIZE}")

def gesture_callback(param):
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


def success():
    lights.lb_system_animation("yes_confirmed")
    audio.play_foreground("success.wav")

def failure():
    lights.lb_system_animation('no_failed')
    audio.play_background("fail.wav")

def select_target_gesture():
    target = 0#random.randint(0,4)
    if target == 0:
        target_gesture = "flick"
        audio.play_background("flick.wav")

if __name__ == '__main__':
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
   
    while(1):
        select_target_gesture()
        time.sleep(random.randint(1,4))
        if not gesture_completed:
            failure()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.pause()

