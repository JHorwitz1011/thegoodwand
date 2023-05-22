
import time
import signal
import json
from multiprocessing import Process
import subprocess
import logging

import sys
import os
sys.path.append(os.path.expanduser('~/thegoodwand/templates'))

#from MQTTObject import MQTTObject
from Services import *
from log import log

import helper

DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)



# NFC_TOPIC = "goodwand/ui/controller/nfc"
# BUTTON_TOPIC = "goodwand/ui/controller/button"
# LIGHT_TOPIC = "goodwand/ui/view/lightbar"
# AUDIO_TOPIC = "goodwand/ui/view/audio_playback"



# audio_pkt = {
#     "header": { "type": "UI_AUDIO", "version": 1},
#     "data": {
#      	"action": "START", 
# 	 	"path": os.getcwd(),
# 	 	"file": "",
#         "mode": "background"
#         }
# }

# light_pkt = {
#             "header": {"type": "UI_LIGHTBAR","version": 1},
#             "data": {
#                 "granularity": 1,
#                 "animation": "power_off",
# 				"path": os.getcwd(),
#         		"crossfade": 0
#             }
#         }

class TGWConductor():
    """
    starts and stops games off of NFC commands
    currently details:
    data record with 

    action: stop
    data: data realted to game

    """

    CONDUCTOR_CLIENT_ID = "TGWConductor"

    def __init__(self):
        #super().__init__()
        
        self.runningSpell = "" 
        self.child_process = None
        self.current_game = ""

        self.mqtt_obj = MQTTClient()
        self.mqtt_client = self.mqtt_obj.start(self.CONDUCTOR_CLIENT_ID)

        self.audio = AudioService(self.mqtt_client, os.getcwd())

        self.lights = LigherService(self.mqtt_client, os.getcwd())

        self.button = ButtonService(self.mqtt_client)
        self.button.subscribe(self.on_button_press)

        self.nfc = NFCService(self.mqtt_client)
        self.nfc.subscribe(self.on_nfc_scan)

    def _kill_game(self):
        # kills current game
        logger.info("Killing Process")
        self.child_process.kill()
        self.child_process = None
        self.audio.stop()
        self.lights.play_lb_csv_animation('app_stopped.csv')
        self.audio.play_background('app_stopped.wav')
        self.runningSpell = ""
        

    #Handles button events
    def on_button_press(self, press):

        if press == 'medium':
            if self.child_process is not None:
                logger.info("Medium button press")
                self._kill_game() 
            else:
                #Long press while idle - what should the behavior be?
                logger.info("Medium press while idle")
            

    def _start_game(self, game: str, game_args):
        """
        starts game. assumes path is valid per helper.fetch_game checking
        """
        logger.debug("Start game called")
        
        filePath = helper.fetch_game(game)
        filePathandMain = filePath + "/main.py"
        
        if filePath is not None:
            logger.debug(f"Playing app start animation")
            self.lights.play_lb_csv_animation('app_launch.csv')
            logger.debug(f"Launching spell: {game} : {filePath} : {game_args}")
            self.child_process = subprocess.Popen(['python3', filePathandMain, filePath, game_args ] )
            logger.debug(f"[SUBPROCESS ID] {self.child_process.pid}")
            
        else:
            logger.debug("invalid game found...")

    def on_nfc_scan(self, records):
        """
        handles logic for starting games
        """
        logger.debug("[NFC SCAN] Scan event")
        payload = json.loads(msg.payload)
        
        try:
            if len(records) > 0:
                cardRecord0 = payload_url = records[0]
                game_on_card = ""
                game_args = ""
                # ADD here to past rest of URL to launch the game with so Yoto can play the card
                recordString = cardRecord0 ["data"]
                
                if recordString == "https://www.thegoodwand.com":
                    logger.debug("[NFC SCAN] The Good Wand Card")
                    cardData = payload['card_data']['records'][1]["data"]
                    card_dict = json.loads(cardData)
                    game_on_card = card_dict ["spell"]
                    logger.debug (f"[SPELL] {game_on_card}      [RUNNING] {self.runningSpell}")
                else:
                    # Wasnt a TGW card, so lets check if Yoto
                    logger.info("[NFC SCAN] NOT a TGW card. Checking if Yoto") 
                    if recordString[0:16]== "https://yoto.io/":
                        game_on_card = "yoto"
                        game_args = recordString [16:]
                        logger.debug (f"Activating Yoto with args {game_args}")
                    else:
                        logger.debug (f"Not a Yoto card. Conductor should handle")
                
                logger.debug (f"Now checking if a spell is to be activated")
                if game_on_card != "":
                    if self.runningSpell != game_on_card:
                        # This is a different spell then running spell, so start it:
                        if self.child_process is None: #no game is running so just start new game
                            self._start_game(game_on_card, game_args)
                        else:
                            # Stop currently running game
                            self._kill_game ()
                            self._start_game(game_on_card, game_args)                        

                        # Update runningSpell. NOT HANDLING edge condition of spells failing to start
                        self.runningSpell = game_on_card
                    else:  
                        logger.debug("[NFC SCAN] Spell already running")                
                else:
                    logger.debug (f"Not a TGW or Yoto cards. Do nothing")
            else:
                logger.debug('[NFC SCAN] No records')
        except:
            logger.warning('[NFC SCAN] JSON parsing error')

    def run(self):
        time.sleep(1) # Just in case the light service is not running. 
        self.lights.play_lb_csv_animation('power_on.csv')
        #TODO Get power on audio
        # self.audio.play_background('power_on.wav')
        signal.pause()


if __name__ == '__main__':
    service = TGWConductor()  
    #logger.debug ("Conductor starting in __name")
    service.run() 