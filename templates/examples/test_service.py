""" Unit tests for Service Files """
import sys, os, time, signal

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from Services import MQTTClient
from Services import ButtonService
from Services import LightService
from Services import AudioService
from Services import NFCService
from Services import IMUService
from log import log

DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)

MQTT_CLIENT_ID = "unit_test"


def button_callback(press, count):
    # User Code Here
    #logger.debug(f"Recieved Press id:{press} count:{count}")
    
    # Supported button types 
    # Note some of these will be reserved for system actions
    # Follow development guides when using 
    if press == button.SHORT_ID:
        logger.debug("short press")
    elif press == button.MEDIUM_ID:
        logger.debug("medium press")
    elif press == button.LONG_ID:
        logger.debug("long press")
    elif press == button.SHORT_MULTI_ID:
        logger.debug(f"Multiple short presses {count}")
    elif press == button.SHORT_MEDIUM_ID:
        logger.debug(f"A short followed by a medium press {count}")
    else:
        logger.debug("Unknown ID")
        

def nfc_callback(records):
    logger.debug(f"NFC Callback {records}")


def orientation_callback(orientation):
    logger.debug(f"IMU orientation {orientation}")

def imu_stream_callback(stream):
    logger.debug(f"IMU stream {stream}")


def imu_on_wake_callback(wake_status:'bool'):

    if wake_status == True: 
        logger.debug(f"Wand is active {wake_status}")
    elif wake_status == False: 
        logger.debug(f"Wand is inactive {wake_status}")
    else:    
        logger.debug(f"Unknown active state {wake_status}")



# Initialize button. return button object
def init_button(mqtt_client, callback):
    button = ButtonService(mqtt_client)
    button.subscribe(button_callback)
    return button 

# Initialize Lights. return Light object
def init_lights(mqtt_client): 
    # If all the light animations are in the same path, set a defult path on init
    # Path can be overrode in the play_lb_csv_animation method. 
    return LightService(mqtt_client = mqtt_client, path = os.getcwd())

def init_audio(mqtt_client):
    return AudioService(mqtt_client = mqtt_client, path = os.getcwd())

def init_nfc(mqtt_client, callback):
    nfc = NFCService(mqtt_client)
    nfc.subscribe(callback)
    return nfc

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
    logger.debug("system test begin")
    
    # Connect to MQTT and get client instance 
    mqtt_object = MQTTClient()
    mqtt_client = mqtt_object.start(MQTT_CLIENT_ID)

    logger.debug("Button setup, Press button.")
    button = init_button(mqtt_client, button_callback)
    
    logger.debug("Light Test")
    lights = init_lights(mqtt_client)
    lights.play_lb_csv_animation("yipee.csv")

    
    # logger.debug("Audio Test")
    # time.sleep(1)
    # audio = init_audio(mqtt_client)
    # audio.play_background("2SPLfltup-horn.wav")
    # audio.play_foreground("2SPLfltup-drum.wav")

    # time.sleep(2)
    # audio.stop()

    # logger.debug("NFC setup, tap nfc card")
    # init_nfc(mqtt_client, nfc_callback)

    # logger.debug("IMU setup, Move Wand")
    # imu =init_imu(mqtt_client,  orientation_cb= orientation_callback,\
    #                imu_stream_cb= imu_stream_callback, on_wake_cb = imu_on_wake_callback)
    # imu.enable_stream()
    # time.sleep(5)
    # imu.disable_stream()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()

