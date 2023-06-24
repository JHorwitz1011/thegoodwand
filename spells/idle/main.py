""" Unit tests for Service Files """
import sys, os, time, signal, math
from collections import deque

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from Services import MQTTClient
from Services import ButtonService
from Services import LightService
from Services import AudioService
from Services import IMUService
from tgw_timer import tgw_timer as Idle_Timer
from log import log

DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)

MQTT_CLIENT_ID = "idle_SPELL"

idleStep = 1
IDLE_NUMBER_STEPS = 4
IDLE_DELAY = 120 # 2 min
idleLightRed = 255    #Gold
idleLightGreen = 215  #Gold
idleLightBlue = 0     #Gold


# Receives "short", "medium", "long"
def button_callback(press):
    # User Code Here
    logger.debug(f"Recieved Press {press}")
    
        
def orientation_callback(orientation):
    logger.debug(f"IMU orientation {orientation}")


def display_lights(red,green,blue):
    lights.lb_block(red,green,blue)

def idle_timer_callback():
    global idleStep
    #global IDLE_NUMBER_STEPS

    fileToPlay = "jmng"+str(idleStep)+".wav"
    logger.debug(f"idle timer expired at step {idleStep} playing {fileToPlay}")
    audio.play_background (fileToPlay)

    idleStep += 1
    if idleStep < IDLE_NUMBER_STEPS:
        lights.lb_csv_animation("idleDrumsShort.csv")
        idle_timer.stop()
        idle_timer.start()
        logger.debug(f"restarting idle time for next step")
    else: 
        logger.debug(f"Last idle step. Terminating")
        lights.lb_csv_animation("idleDrumsLong.csv")
        os._exit(0)
    


def imu_on_wake_callback(wake_status:'bool'):
    if wake_status == True: 
        logger.debug(f"Wand is active, terminate idle spell")
        time.sleep(10)
        lights.lb_block(0,0,0)
        os._exit(0)

    elif wake_status == False: 
        logger.debug(f"Wand is inactive, activate")
        audio.play_background ("activateIdle.wav")
        display_lights (idleLightRed, idleLightGreen,idleLightBlue) 
        idle_timer.start()

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

def init_imu(mqtt_client, on_wake_cb):
    imu = IMUService(mqtt_client)
    imu.subscribe_on_wake(on_wake_cb)
    return imu

# Cleanup 
def terminate_spell(sig, frame): 
    logger.debug("Terminating Idle Spell")
    lights.lb_block(0,0,0)
    time.sleep(.1)
    os._exit(0)
    

if __name__ == '__main__':
    # Connect to MQTT and get client instance 
    logger.debug("Starting idle spell")
    mqtt_object = MQTTClient()
    mqtt_client = mqtt_object.start(MQTT_CLIENT_ID)

    # Get spell activation arguments. #1 is path, #2 is other args
    param_1 = ""
    param_2 = ""
    if len(sys.argv) > 1 :
        param_1= sys.argv[1] 
    
    if len(sys.argv) > 2 :
        param_2= sys.argv[2] 

	    
    # if started by conductor, param1 is the path,
	# otherwise use cwd
    
    if param_1 !="":
        spellPath = param_1
    else:
        spellPath =os.getcwd() 

    audio   = init_audio(mqtt_client, spellPath)
    button  = init_button(mqtt_client, button_callback)
    lights  = init_lights(mqtt_client, spellPath)
    imu     = init_imu(mqtt_client, on_wake_cb = imu_on_wake_callback)

    idle_timer = Idle_Timer(IDLE_DELAY, idle_timer_callback, name ="idle timer") 
       
    audio.play_foreground("activatingIdle.wav")
    
    signal.signal(signal.SIGINT, terminate_spell)
    signal.signal(signal.SIGTERM, terminate_spell)
    logger.debug("Idle Init done. Waiting for events")
    idle_timer.start()
    signal.pause()

