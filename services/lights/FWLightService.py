# python 3.6

import json
import time
import neopixel
import board
import csv
import os
import math
import sys
import logging
from paho.mqtt import client as mqtt_client

broker = 'localhost'
port = 1883
lightbar_topic = "goodwand/ui/view/lightbar"
main_led_topic = "goodwand/ui/view/main_led"

client_id = 'TGW-LightService'
NUM_LEDS = 21
PIN = board.D12
ORDER = neopixel.GRB
DEFAULT_CROSSFADE_LENGTH = 0.2 #s
DEFAULT_SAMPLING_RATE = 30 #hz

## Logger configuration
## Change level by changing DEBUG_LEVEL variable to ["DEBUG", "INFO", "WARNING", "ERROR"]
DEBUG_LEVEL = "DEBUG"
LOGGER_HANDLER=sys.stdout
LOGGER_NAME = __name__
LOGGER_FORMAT = '[%(filename)s:%(lineno)d] %(levelname)s:  %(message)s'

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.getLevelName(DEBUG_LEVEL))

handler = logging.StreamHandler(LOGGER_HANDLER)
handler.setLevel(logging.getLevelName(DEBUG_LEVEL))
format = logging.Formatter(LOGGER_FORMAT)
handler.setFormatter(format)
logger.addHandler(handler)



systemAnimations = {
    "yipee": "yipee.csv",
    "yes": "yes_confirmed.csv",
    "no": "no_failed.csv",
    "confused": "confused_not_understood.csv",
    "up_down": "green_up_down.csv"
}

EMPTY_LIGHTS = [(0,0,0)]*20

display_to_hardware_adapter = {
        0:1,
        1:20,
        2:2,
        3:19,
        4:3,
        5:18,
        6:4,
        7:17,
        8:5,
        9:16,
        10:6,
        11:15,
        12:7,
        13:14,
        14:8,
        15:13,
        16:9,
        17:12,
        18:10,
        19:11,
    }

def grab_animation_from_csv(filepath):
    animation = []
    color = []
    lengths = []
    try:
        file = open(filepath, newline='')
        for row in csv.reader(file, delimiter=',', quotechar='|'):
            animation.append(row)

        for a in animation:
            lengths.append(float(a[0])/1000)
        for a in animation:
            color.append(a[1:])
        for data in color:
            for index in range(len(data)):
                data[index] = int(data[index][1:], 16)
    except KeyError:
        logger.debug(f"ERROR: {filepath} not found")
    return lengths, color

class FWLightService():
    #set constants and the such
    def __init__(self, pin=PIN, fs=60):
        self.fs = fs
        self.pixels = neopixel.NeoPixel(pin, NUM_LEDS)
        self.animation_queue = []
        self.empty = True
        self.indicatorColor = (255,255,255)
        self.indicatorAnimation = 'pulse'
        logger.debug("Lightbar Finished __init")
     
    ############### MQTT ###############################
    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.debug("Lightbar Connected to MQTT Broker!")
            else:
                logger.debug(f"Failed to connect Lightbar to MQTT server, return code {rc}")

        client = mqtt_client.Client(client_id)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client

    def on_lightbar_message(self, client, userdata, msg):
        self.empty = False
        payload = json.loads(msg.payload)
        logger.debug(f"Lightbar message rcvd")
        try:
            animationName = payload['data']['animation']
            anomationPath = payload['data']['path']
            try:
                animationFile = systemAnimations[animationName]
            except KeyError: 
                animationFile = anomationPath + "/" + animationName  
  
            if os.path.isfile(animationFile):
                self.animation_queue.append(grab_animation_from_csv(animationFile))
                logger.info(f'Lightbar animation added: {animationFile}')
            else:
                logger.error(f'animation file not found {animationFile}')
    
       
        except KeyError:
            logger.warning("ERROR: Invalid Animation file key error:",msg)

    def on_main_led_message(self, client, userdata, msg):
        payload = json.loads(msg.payload)
        logger.debug(f"Lightbar System LED message rcvd with {str(paylod)}")
        try:
            self.pixels[0] = tuple(payload["data"]["color1"])
        except KeyError:
            logger.warning("ERROR: Invalid MAIN LED Animation")

    ################## MAIN LOOP ##########################
    def run(self):
        client = self.connect_mqtt()
        client.message_callback_add(lightbar_topic, self.on_lightbar_message)
        client.message_callback_add(main_led_topic, self.on_main_led_message)

        client.subscribe(lightbar_topic)
        client.subscribe(main_led_topic)
        client.enable_logger()
        client.loop_start()
        
        while True:
            if self.animation_queue:
                self.empty = False
                try:
                    animation = self.animation_queue.pop(0)
                    self.animate_blocking(animation[1], animation[0])
                except:
                    logger.warning(f"Frame not played")
            elif not self.empty:
                self.current_frame = EMPTY_LIGHTS
                self.update_strip(EMPTY_LIGHTS)
                self.empty=True
                logger.debug(f'Done playing Animation. Turning LEDs off')
            else:
                time.sleep(.05)



    ################# LIGHT HANDLING ######################
    def animate_blocking(self, colordata, lengthdata):
        for x in range(len(colordata)):
            self.current_frame = colordata[x]
            self.update_strip(colordata[x])
            time.sleep(lengthdata[x])

    def update_strip(self, display_frame):
        for x in range(len(display_frame)):
            self.pixels[display_to_hardware_adapter[x]] = display_frame[x]
        self.pixels.show()


if __name__ == '__main__':
    logger.debug ("Light Service starting")
    service = FWLightService()  
    service.run() 
