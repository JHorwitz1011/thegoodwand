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

        self.bat_current_fault = None
        self.bat_current_status = None
        self.listening = False

        self.mqtt_obj = MQTTClient()
        self.mqtt_client = self.mqtt_obj.start(self.CONDUCTOR_CLIENT_ID)

        self.audio = AudioService(self.mqtt_client, os.getcwd())

        self.lights = LightService(self.mqtt_client, os.getcwd())

        self.button = ButtonService(self.mqtt_client)
        self.button.subscribe(self.on_button_press)

        self.nfc = NFCService(self.mqtt_client)
        self.nfc.subscribe(self.on_nfc_scan)

        self.charger = ChargerService(self.mqtt_client)
        self.charger.on_fault(self.charger_on_fault)
        self.charger.on_status(self.charger_on_status)

    def update_state(self):
        if self.listening:
            pass
        elif self.bat_current_fault == "hot":
            pass
        elif self.bat_current_status == "fast charging":
            pass
        elif self.bat_current_status == "complete":
            pass
        else:
            pass

    def keyword_on_message(self, keyword):
        # start game
        pass

    def imu_on_message(self, msg):
        # do stuff
        self.update_state()

    def charger_on_fault(self,fault):
        if fault == 0: 
            logger.debug("Temperature Normal")
            self.bat_current_fault = None
        elif fault == 1:
            logger.debug("Temperature Hot")
            self.bat_current_fault = "hot"
        elif fault == 2:
            logger.debug("Temperature Cold")
            self.bat_current_fault = "cold"
        else:
            logger.debug("Unknown Fault")
            self.bat_current_fault = "unknown"
        
        self.update_button_led()
    
    def charger_on_status(self, status):
        if status == 0: 
            logger.debug("Not charging")
            self.bat_current_status = None
        elif status == 0x10:
            logger.debug("Pre Charge")
            self.bat_current_status = "pre charge"
        elif status == 0x20:
            logger.debug("Fast Charging")
            self.bat_current_status = "fast charging"
        elif status == 0x30:
            logger.debug("Charge Complete")
            self.bat_current_status = "complete"
        else:
            logger.debug("Unknown Status")
            self.bat_current_status = "unknown"

        self.update_button_led()

    def _kill_game(self):
        # kills current game
        logger.info(f"Killing Process {self.child_process.pid}")
        #self.child_process.kill()
        os.kill(self.child_process.pid, signal.SIGTERM)
        self.child_process = None
        self.audio.stop()
        self.lights.play_lb_csv_animation('app_stopped.csv')
        self.audio.play_background('app_stopped.wav')
        self.runningSpell = ""
        self.update_state()

    #Handles button events
    def on_button_press(self, press):

        if press == 'medium':
            if self.child_process is not None:
                logger.info("Medium button press. Killing Spell")
                self._kill_game() 
            else:
                #Long press while idle - what should the behavior be?
                logger.info("Medium press while idle")
            

    def _start_game(self, game: str, game_args):
        """
        starts game. assumes path is valid per helper.fetch_game checking
        """
        logger.debug(f"Start game called {game}  args {game_args}")
        
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
            self.runningSpell = ""
        
        self.update_state()

    def on_nfc_scan(self, records):
        """
        handles logic for starting games
        """
        logger.debug(f"[NFC SCAN] records: {records}")
        try:
            if len(records['card_data']['records']) > 0:
                cardRecord0 = payload_url = records['card_data']['records'][0]
                game_on_card = ""
                game_args = ""
                # ADD here to past rest of URL to launch the game with so Yoto can play the card
                recordString = cardRecord0 ["data"]
                
                if recordString == "https://www.thegoodwand.com":
                    logger.debug("[NFC SCAN] The Good Wand Card")
                    cardData = records['card_data']['records'][1]["data"]
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
        except Exception as e:
            logger.warning(f'[NFC SCAN] JSON parsing error: {e}')

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