
import time
import signal
import json
from multiprocessing import Process
import subprocess
import sys
import os
import logging
import threading
import math


sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from MQTTObject import MQTTObject
import helper

NFC_TOPIC = "goodwand/ui/controller/nfc"
BUTTON_TOPIC = "goodwand/ui/controller/button"
GESTURE_TOPIC = "goodwand/ui/controller/gesture"
LIGHT_TOPIC = "goodwand/ui/view/lightbar"
AUDIO_TOPIC = "goodwand/ui/view/audio_playback"
UV_TOPIC = "goodwand/ui/view/uv"

SPELL_CLIENT_ID = "Pooftos"

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


audio_pkt = {
    "header": {
      "type": "UI_AUDIO", "version": 1
    },
    "data": {
     	"action": " ", 
	 	"path": " ",
	 	"file": " ",
		"mode": " "
    }
}

light_pkt = {
            "header": {"type": "UI_LIGHTBAR","version": 1},
            "data": {
                "granularity": 1,
                "animation": "power_off",
				"path": os.getcwd(),
        		"crossfade": 0
            }
        }

uv_pkt = {
            "header": {"type": "UI_UV","version": 1},
            "data": {
                "timeOn": 5,
            }
        }

class Pooftos(MQTTObject):
    global oldOrient
    global currentPath

    def __init__(self):
        super().__init__()

        self.callbacks = {
            NFC_TOPIC : self.on_nfc_scan,
            BUTTON_TOPIC: self.on_button_press,
            GESTURE_TOPIC: self.on_gesture,
        }

    def play_audio(self, file, playMode):
        logger.info(f"Play audio file {file}")
        audio_pkt ['data']['action'] = "START"
        audio_pkt ['data']['file'] = file
        audio_pkt ["data"]["mode"] = playMode 
        self.publish(AUDIO_TOPIC, json.dumps(audio_pkt))
    
    def stop_audio(self):
        logger.info(f"[Audio] stop all")
        audio_pkt ['data']['action'] = "STOP"
        self.publish(AUDIO_TOPIC, json.dumps(audio_pkt))

    def play_light(self, lightEffect):
	    light_pkt ['data']['animation'] = lightEffect
	    logger.info(f"Light Effect {lightEffect}")
	    self.publish(LIGHT_TOPIC, json.dumps(light_pkt))

    def deactivate_tv (self):
        global currentPath
        self.play_audio ("deactive.wav", "background")
        self.play_light ("deactive.csv")
        os.system("sh "+currentPath + "/Pooftos.sh "+ currentPath )

    #Handles Gesture events
    def on_gesture(self, client, userdata, msg):
        global oldOrient
        payload = json.loads(msg.payload)
        newOrientation =   payload['data']["orientation"]
        newOrient = int(math.log(newOrientation,2))

        if (newOrient == 5) and (oldOrient == 3): # 5=flt-up
            self.deactivate_tv()
        
        oldOrient = newOrient

    def on_button_press(self, client, userdata, msg):
        payload = json.loads(msg.payload)
        keyPressType = payload['data']['event'] 
        
        if keyPressType == 'short':
            self.deactivate_tv()

    def on_nfc_scan(self, client, userdata, msg):
        """
        handles logic for starting games
        """
        payload = json.loads(msg.payload)
        if len(payload['card_data']['records']) > 0:
            cardRecord0 = payload_url = payload['card_data']['records'][0]
            if cardRecord0 ["data"] == "https://www.thegoodwand.com":
                cardRecord1 = payload['card_data']['records'][1]
                cardData = cardRecord1 ["data"]
                card_dict = json.loads(cardData)
                try:
                    game_on_card = card_dict ["spell"]
                    logger.debug (f"spell is: {game_on_card}")
                    # Need to add code that:
                    if game_on_card == "pooftos":
                        logger.info (f"re activating pooftos through NFC")
                        #What should we do here
                                        
                except:
                    logger.debug (f"Not a spell")

        else:    
            logger.debug(f'No records found on NFC card')

    def run(self):
        global currentPath
        logger.debug(f'Pooftos spell started')
        self.start_mqtt(SPELL_CLIENT_ID, self.callbacks)
        
        param_1 = ""
        param_2 = ""
		
		# TODO: Not the way to check for arguments
        try:
            param_1= sys.argv[1] 
            param_2= sys.argv[2] 
        except:
            logger.error ("no args")

		# if started by conductor, param1 is the path,
		# otherwise use cwd
        if param_1 !="":
            currentPath = param_1
        else:
        	currentPath =os.getcwd() 
    
        logger.debug(f'Pooftos spell path is{currentPath}')
        audio_pkt ['data']['path'] = currentPath
        light_pkt ['data']['path'] = currentPath
        self.play_audio ("activating-pooftos.wav", "background")
        signal.pause()


if __name__ == '__main__':
    service = Pooftos()  
    service.run() 