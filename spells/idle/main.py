""" Unit tests for Service Files """
import sys, os, time, signal

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from Services import MQTTClient
from Services import LightService
from Services import AudioService
from Services import IMUService
from tgw_timer import tgw_timer as Idle_Timer
from log import log

DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)

MQTT_CLIENT_ID = "idle_SPELL"
TERMINATION_DELAY = 18 # final audio is 16 seconds. lights is 14.5s


IDLE_NUMBER_STEPS = 4
IDLE_DELAY = 120 # 2 min
idleLightRed = 255    #Gold
idleLightGreen = 215  #Gold
idleLightBlue = 0     #Gold


class Idle():
    def __init__(self) -> None:
        self.idle_step = 1
        self.timer = Idle_Timer(IDLE_DELAY, self.timer_callback, name ="idle timer") 

    def start(self):
        logger.debug("starting idle sequence ")
        #audio.play_background ("activateIdle.wav") # Dont think we need this 
        self.timer.start()
        
    def wait(self):
        logger.debug("Idle Init done. Waiting for idle event")
        audio.play_foreground("activatingIdle.wav")
        lights.lb_csv_animation("idleDrumsShort.csv")

    def timer_callback(self):
        logger.debug(f"idle timer expired. Idle Step:{self.idle_step}")
        audio.play_background (f"jmng{self.idle_step}.wav")
        if self.idle_step < IDLE_NUMBER_STEPS:
            lights.lb_csv_animation("idleDrumsShort.csv")
            self.timer.start()
        else: 
            lights.lb_csv_animation("idleDrumsLong.csv")
            delayed_terminnation(TERMINATION_DELAY)

        self.idle_step += 1


def display_fire(red,green,blue):
    lights.lb_fire(red,green,blue)

def imu_on_wake_callback(wake_status:'bool'):
    if wake_status == True: 
        logger.debug(f"Wand is active")
        idle_spell.timer.stop()
        delayed_terminnation(0)

    elif wake_status == False: 
        logger.debug(f"Wand is inactive")
        idle_spell.start()

def init_imu(mqtt_client, on_wake_cb):
    imu = IMUService(mqtt_client)
    imu.subscribe_on_wake(on_wake_cb)
    return imu

def delayed_terminnation(delay):
    logger.debug(f"Terminating idle spell: Delay {delay}")
    if delay: time.sleep(delay) # Delay to allow final animation to finish
    logger.debug("Terminating Idle Spell")
    lights.lb_clear()
    audio.stop()
    time.sleep(.25)
    os._exit(0)

def sig_callback(sig, frame):
    idle_spell.timer.stop()
    delayed_terminnation(0)

def get_path():
    param_1 = None
    if len(sys.argv) < 2:
        logger.debug("No arguments provided.")
    else:
        param_1 = sys.argv[1]
    return param_1 if param_1 else os.getcwd()


if __name__ == '__main__':
    # Connect to MQTT and get client instance 
    logger.debug("Starting idle spell")
    mqtt_object = MQTTClient()
    mqtt_client = mqtt_object.start(MQTT_CLIENT_ID)
    spellPath = get_path()

    audio   = AudioService(mqtt_client, spellPath)
    lights  = LightService(mqtt_client, spellPath)
    imu     = init_imu(mqtt_client, imu_on_wake_callback)

    idle_spell = Idle()
    # possible bug at the wait state if the wand is alreay in idle. 
    # This will be fixed when the conductor handles the idle / launching of this spell
    idle_spell.wait() 
    signal.signal(signal.SIGINT, sig_callback)
    signal.signal(signal.SIGTERM, sig_callback)
    signal.pause()

