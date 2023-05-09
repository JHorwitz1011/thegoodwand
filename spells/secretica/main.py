
import time
import signal
import json
from multiprocessing import Process
import subprocess
import sys
import os
import logging
import threading


sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from MQTTObject import MQTTObject
import helper

NFC_TOPIC = "goodwand/ui/controller/nfc"
BUTTON_TOPIC = "goodwand/ui/controller/button"
LIGHT_TOPIC = "goodwand/ui/view/lightbar"
AUDIO_TOPIC = "goodwand/ui/view/audio_playback"
UV_TOPIC = "goodwand/ui/view/uv"

SPELL_CLIENT_ID = "Secretica"

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

class Secretica(MQTTObject):

    def __init__(self):
        super().__init__()

        self.callbacks = {
            NFC_TOPIC : self.on_nfc_scan,
            BUTTON_TOPIC: self.on_button_press,
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

    def activate_uv(self):
        uvStartTime = time.strftime("%M:%S +000")
        logger.info (f"Start  activate {uvStartTime}")
        uv_pkt ['data']['timeOn'] = 8
        self.publish(UV_TOPIC, json.dumps(uv_pkt))
        self.play_audio ("uv_activated.wav", "background")
        self.play_light ("uv_activated.csv")
        

    #Handles button events
    def on_button_press(self, client, userdata, msg):
        payload = json.loads(msg.payload)
        keyPressType = payload['data']['event'] 
        
        if keyPressType == 'short':
            self.activate_uv()

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
                    if game_on_card == "secretica":
                        logger.info (f"re activating secretica through NFC")
                        self.activate_uv() 
                        
                    # if the spell=secretica, then turn UV light on for 20 seconds
                    # LED effect of 20 seconds goes from all LEDs to none
                    # Turn off UV Light
                    # play humming audio in the background
                
                except:
                    logger.debug (f"Not a spell")

        else:    
            logger.debug(f'No records found on NFC card')

    def run(self):
        logger.debug(f'Secretica spell started')
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
    
        logger.debug(f'Secretica spell path is{currentPath}')
        audio_pkt ['data']['path'] = currentPath
        light_pkt ['data']['path'] = currentPath
        self.play_audio ("secretica.wav", "background")
        signal.pause()


if __name__ == '__main__':
    service = Secretica()  
    service.run() 