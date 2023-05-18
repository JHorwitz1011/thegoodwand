
import time
import signal
import json
from multiprocessing import Process
import subprocess
import logging

import sys
import os
sys.path.append(os.path.expanduser('~/thegoodwand/templates'))

from MQTTObject import MQTTObject
import helper

NFC_TOPIC = "goodwand/ui/controller/nfc"
BUTTON_TOPIC = "goodwand/ui/controller/button"
LIGHT_TOPIC = "goodwand/ui/view/lightbar"
AUDIO_TOPIC = "goodwand/ui/view/audio_playback"

CONDUCTOR_CLIENT_ID = "TGWConductor"

## Logger configuration
## Change level by changing DEBUG_LEVEL variable to ["DEBUG", "INFO", "WARNING", "ERROR"]
DEBUG_LEVEL = "INFO"
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
    "header": { "type": "UI_AUDIO", "version": 1},
    "data": {
     	"action": "START", 
	 	"path": os.getcwd(),
	 	"file": "",
        "mode": "background"
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

#maximum allowed time a button event can register upon nfc tag scan
MAX_BUTTON_LAG = .5 # seconds

class TGWConductor(MQTTObject):
    """
    starts and stops games off of NFC commands
    currently details:
    data record with 

    action: stop
    data: data realted to game

    """
    def __init__(self):
        super().__init__()
        
        self.runningSpell = "" 

        self.child_process = None
        self.time_since_short_press = time.time()
        self.time_since_long_press = time.time()
        self.current_game = ""
        self.sub = None

        self.callbacks = {
            NFC_TOPIC : self.on_nfc_scan,
            BUTTON_TOPIC: self.on_button_press,
        }
        
	
    def play_light(self, lightEffect):
        light_pkt ['data']['animation'] = lightEffect
        light_pkt ['data']['path'] = os.getcwd() 
        logger.debug(f"Playing Light Effect {lightEffect}  in {light_pkt['data']['path']}" )
        self.publish(LIGHT_TOPIC, json.dumps(light_pkt))
    
    def play_audio(self, file):
        logger.debug ("Playing" , file)
        audio_pkt ['data']['action'] = "START"
        audio_pkt ['data']['file'] = file
        audio_pkt ['data']['path'] = os.getcwd()
        self.publish(AUDIO_TOPIC, json.dumps(audio_pkt))
    
    def stop_audio(self):
        logger.info(f"[Audio] stop all")
        audio_pkt ['data']['action'] = "STOP"
        self.publish(AUDIO_TOPIC, json.dumps(audio_pkt))


    def _kill_game(self):
        # kills current game
        logger.info("Killing Process")
        self.child_process.kill()
        self.child_process = None
        self.stop_audio ()
        self.play_light ('app_stopped.csv')
        self.play_audio ('app_stopped.wav')
        self.runningSpell = ""
        

    #Handles button events
    def on_button_press(self, client, userdata, msg):
        payload = json.loads(msg.payload)
        keyPressType = payload['data']['event'] 
        if keyPressType == 'medium':
            if self.child_process is not None:
                logger.info("Medium button press")
                self._kill_game() 
            else:
                #Long press while idle - what should the behavior be?
                logger.info("Medium press while idle")
            

    def _start_game(self, game: str):
        """
        starts game. assumes path is valid per helper.fetch_game checking
        """
        logger.debug("Start game called")
        
        filePath = helper.fetch_game(game)
        filePathandMain = filePath + "/main.py"
        
        if filePath is not None:
            logger.debug(f"Playing app start animation")
            self.play_light ('app_launch.csv')
            logger.debug(f"Launching spell: {game} {filePath}")
            self.child_process = subprocess.Popen(['python3', filePathandMain, filePath ] )
            logger.debug(f"[SUBPROCESS ID] {self.child_process.pid}")
            
        else:
            logger.debug("invalid game found...")

    def on_nfc_scan(self, client, userdata, msg):
        """
        handles logic for starting games
        """
        logger.debug("[NFC SCAN] Scan event")
        payload = json.loads(msg.payload)
        
        try:
            if len(payload['card_data']['records']) > 0:
                cardRecord0 = payload_url = payload['card_data']['records'][0]
                
                if cardRecord0 ["data"] == "https://www.thegoodwand.com":
                    logger.debug("[NFC SCAN] The Good Wand Card")
                    cardData = payload['card_data']['records'][1]["data"]
                    card_dict = json.loads(cardData)
                    game_on_card = card_dict ["spell"]
                    logger.debug (f"[SPELL] {game_on_card}      [RUNNING] {self.runningSpell}")
                    
                    if self.runningSpell != game_on_card:
                        # This is a different spell then running spell, so start it:
                        if self.child_process is None: #no game is running so just start new game
                            self._start_game(game_on_card)
                        else:
                            # Stop currently running game
                            self._kill_game ()
                            self._start_game(game_on_card)                        

                        # Update runningSpell. NOT HANDLING edge condition of spells failing to start
                        self.runningSpell = game_on_card
                    else:  
                        logger.debug("[NFC SCAN] Spell already running")                
                else:
                        logger.debug("[NFC SCAN] NOT a TGW card") 
                        # Add here support for identifying Yoto and starting it
            else:
                logger.debug('[NFC SCAN] No records')
        except:
            logger.warning('[NFC SCAN] JSON parsing error')

    def run(self):
        #logger.debug ("Conductor Running self")
        self.start_mqtt(CONDUCTOR_CLIENT_ID, self.callbacks)
        self.play_light ('power_on.csv')
        #logger.debug("Done with init animation")
        signal.pause()


if __name__ == '__main__':
    service = TGWConductor()  
    #logger.debug ("Conductor starting in __name")
    service.run() 