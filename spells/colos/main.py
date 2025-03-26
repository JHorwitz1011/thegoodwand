""" Unit tests for Service Files """
import sys, os, time, signal, math
from collections import deque

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from Services import MQTTClient
from Services import ButtonService
from Services import LightService
from Services import AudioService
from Services import IMUService
from log import log

DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)

MQTT_CLIENT_ID = "COLOS_SPELL"

NORMALIZE = float(255/90)

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


def imu_stream_callback(stream):
    start = time.time()
    accel_mag = magnitude(get_vector(stream['accel']))
    gyro_mag  = int(magnitude(get_vector(stream['gyro'])))
    x, y, z = tilt_angle(get_vector(stream['accel']), accel_mag )
    display_lights(x,y,z)


def imu_on_wake_callback(wake_status:'bool'):

    if wake_status == True: 
        logger.debug(f"Wand is active, enable stream{wake_status}")
        imu.enable_stream()
    elif wake_status == False: 
        logger.debug(f"Wand is inactive, disable stream{wake_status}")
        imu.disable_stream()
    else:    
        logger.warning(f"Unknown active state {wake_status}")

# Initialize button. return button object
def init_button(mqtt_client, callback):
    button = ButtonService(mqtt_client)
    button.subscribe(button_callback)
    return button 

def init_lights(mqtt_client, path): 
    return LightService(mqtt_client = mqtt_client, path = path)

def init_audio(mqtt_client, path):
    return AudioService(mqtt_client = mqtt_client, path = path)

def init_imu(mqtt_client, imu_stream_cb, on_wake_cb):
    imu = IMUService(mqtt_client)
    imu.subscribe_stream(imu_stream_cb)
    imu.subscribe_on_wake(on_wake_cb)
    return imu

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
    # Connect to MQTT and get client instance 
    logger.debug("Starting Colos spell")
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
        spellPath =os.getcwd() 

    audio   = init_audio(mqtt_client, spellPath)
    button  = init_button(mqtt_client, button_callback)
    lights  = init_lights(mqtt_client, spellPath)
    imu     = init_imu(mqtt_client, imu_stream_cb= imu_stream_callback, on_wake_cb = imu_on_wake_callback)
    imu.enable_stream()
   
    audio.play_foreground("activatingColos.wav")
    audio.play_background("colosBkgrnd.wav")

    # Buffer size = smoothing effect 
    # The higher the value the slower the colors will change 
    # Dont make it too high or the color will be white most the time. 
    buffer_size = 6
    x_buffer = deque(maxlen=buffer_size)
    y_buffer = deque(maxlen=buffer_size)
    z_buffer = deque(maxlen=buffer_size)
    
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.pause()

