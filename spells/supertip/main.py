""" Unit tests for Service Files """
import sys, os, time, signal, math, random
#from collections import deque

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

SuperTips = [
"AbilitySpeak", 
"DwellDreams",    
"howFarGo",   
"light-chance", 
"NiceSHark", 
"PatiencePad", 
"Squeecy",    
"whoYouChoose",
"BalanceKey",
"FearHate",   
"Infinity", 
"PastCanHeart",
"PatienceWisdom",   
"YoureWizard",
"DontCocky",  
"HaveCourageKind",   
"NeverLookBack",  
"pathNotEase",   
"PlaceLikeHome",
"ToLive" ]

drumRollDuration = 5
pointDelay = 3

numOfTips = len(SuperTips)

MQTT_CLIENT_ID = "SUPERTIP_SPELL"
lastTip = 0
currentTip = 0

        
def orientation_callback(orientation):
    global lastTip
    global lastOrientation
    global lastTime

    gestureTime = time.time()
    deltaTime = gestureTime - lastTime
    lastTime = gestureTime

    logger.debug(f"IMU orientation {orientation} LastTip is {lastTip} and lastOrientation is {lastOrientation} delta time {deltaTime}")
   
    if orientation == 32: #FlatUp

        if lastOrientation == 8: # Only play new one if the last oreintation was point up
            if deltaTime < drumRollDuration:
                #Too fast
                logger.debug(f"Too fast, delta time {deltaTime}")
                audio.play_foreground("patience.wav")
    
            else: 
                if deltaTime > ( drumRollDuration + pointDelay):
                    #Too slow
                    logger.debug(f"Too slow, delta time {deltaTime}")
                    audio.play_foreground("TooSlow.wav")

                else:
                    # Pointed flat at the rignt time
                    currentTip = random.choice (SuperTips)
                    while lastTip == currentTip:
                        currentTip = random.choice (SuperTips)
                    
                    logger.debug(f"Wand Flatup, Playing New tip is {currentTip}" )
                    audio.play_foreground(currentTip+".wav")
                    lastTip = currentTip
        else:
            # repeat the same quote agaiin
            audio.stop()
            audio.play_foreground(currentTip+".wav")
   

    if orientation == 8: #PointUp
        logger.debug(f"Wand pointing up" )
        lights.play_lb_csv_animation ("STdrumRoll.csv")
        audio.play_foreground("stDrumRoll.wav")
        lastOrientation = orientation
        
    if ((orientation == 2) or (orientation == 1)):
        lastOrientation = orientation
        

# Receives "short", "medium", "long"
def button_callback(press):
    # User Code Here
    logger.debug(f"Recieved Press {press}")
    
    # What should we do with short button press
    # if press == "short":


# Initialize button. return button object
def init_button(mqtt_client, callback):
    button = ButtonService(mqtt_client)
    button.subscribe(button_callback)
    return button 

def init_lights(mqtt_client, path): 
    return LightService(mqtt_client = mqtt_client, path = path)

def init_audio(mqtt_client, path):
    return AudioService(mqtt_client = mqtt_client, path = path)

def init_imu(mqtt_client, orientation_cb):
    imu = IMUService(mqtt_client)
    imu.subscribe_orientation(orientation_callback)
    return imu

# Cleanup 
def signal_handler(sig, frame): 
    # Turn off raw data stream
    imu.disable_stream()
    logger.debug("disable stream")
    lights.block(0,0,0)
    time.sleep(.1)
    
    #GPIO.cleanup()
    sys.exit(0)


if __name__ == '__main__':
    # Connect to MQTT and get client instance 
    global lastTime
    global lastOrientation

    logger.debug(f"Starting SuperTip spell")
    mqtt_object = MQTTClient()
    mqtt_client = mqtt_object.start(MQTT_CLIENT_ID)

    # Get out path
    param_1 = ""
    param_2 = ""
	
    logger.debug(f"Arguments len is {len(sys.argv)}")
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
   
    logger.debug(f"path is{spellPath}")

    audio   = init_audio(mqtt_client, spellPath)
    button  = init_button(mqtt_client, button_callback)
    lights  = init_lights(mqtt_client, spellPath)
    imu     = init_imu(mqtt_client,  orientation_cb= orientation_callback)
 
   
    audio.play_foreground("activatingSuperTip.wav")

    lastTime = time.time()
    lastOrientation = 0
    
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    audio.play_foreground("SuperTipActivated.wav")
    signal.pause()

