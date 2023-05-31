""" Unit tests for Service Files """
import sys, os, time, signal, math

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

MQTT_CLIENT_ID = "LIGHT_SPELL"



def magnitude(vector):
    return math.sqrt(sum(pow(element, 2) for element in vector))

# Receives "short", "medium", "long"
def button_callback(press):
    # User Code Here
    logger.debug(f"Recieved Press {press}")
    
    #Example medium button press
    if press == "medium":
        lights.play_lb_csv_animation("yipee.csv")

def orientation_callback(orientation):
    logger.debug(f"IMU orientation {orientation}")

def get_vector(data) -> "vector[3]":
    return [data['x'], data['y'], data['z']]

def tilt_angle(vector,  mag):
    x_norm = vector['x']/mag
    y_norm = vector['y']/mag
    z_norm = vector['z']/mag

    pitch = math.atan2(x_norm, magnitude([y_norm, z_norm]))
    roll= math.atan2(y_norm, magnitude[x_norm,y_norm])
    yaw = math.atan2(magnitude([x_norm,y_norm]), z_norm)
    return roll, pitch, yaw

def imu_stream_callback(stream):
    #logger.debug(f"IMU stream {stream}")
    start = time.time()
    accel_mag = magnitude(get_vector(stream['accel']))
    gyro_mag  = magnitude(get_vector(stream['gyro']))
    roll, pitch, yaw = tilt_angle(stream['accel'])
    end = time.time()


    
    logger.debug(f"Magnitudes Accel : {accel_mag}  Gyro: {gyro_mag}   Time: {end-start}")


def imu_on_wake_callback(wake_status:'bool'):

    if wake_status == True: 
        logger.debug(f"Wand is active, enable stream{wake_status}")
        imu.enable_stream()
    elif wake_status == False: 
        logger.debug(f"Wand is inactive, disable stream{wake_status}")
        imu.disable_stream()
    else:    
        logger.debug(f"Unknown active state {wake_status}")

# Initialize button. return button object
def init_button(mqtt_client, callback):
    button = ButtonService(mqtt_client)
    button.subscribe(button_callback)
    return button 

def init_lights(mqtt_client): 

    return LightService(mqtt_client = mqtt_client, path = os.getcwd())

def init_audio(mqtt_client):
    return AudioService(mqtt_client = mqtt_client, path = os.getcwd())

def init_imu(mqtt_client, orientation_cb, imu_stream_cb, on_wake_cb):
    imu = IMUService(mqtt_client)
    imu.subscribe_orientation(orientation_cb)
    imu.subscribe_stream(imu_stream_cb)
    imu.subscribe_on_wake(on_wake_cb)
    return imu

# Cleanup 
def signal_handler(sig, frame): 
    # Turn off raw data stream
    imu.disable_stream()
    #GPIO.cleanup()
    sys.exit(0)


if __name__ == '__main__':
    # Connect to MQTT and get client instance 
    logger.debug("Starting Light spell")
    mqtt_object = MQTTClient()
    mqtt_client = mqtt_object.start(MQTT_CLIENT_ID)
    audio   = init_audio(mqtt_client)
    button  = init_button(mqtt_client, button_callback)
    lights  = init_lights(mqtt_client)
    imu     =init_imu(mqtt_client,  orientation_cb= orientation_callback,\
                imu_stream_cb= imu_stream_callback, on_wake_cb = imu_on_wake_callback)
    

    
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()

