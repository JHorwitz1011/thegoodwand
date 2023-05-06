
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

DEBUG_LEVEL = "DEBUG"

start_audio_pkt = {
    "header": { "type": "UI_AUDIO", "version": 1},
    "data": {
     	"action": "START", 
	 	"path": os.getcwd(),
	 	"file": ""
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
        
        self.logger = logging.getLogger('tgw_conductor')
        self.logger.addHandler(logging.StreamHandler())
        level = logging.getLevelName(DEBUG_LEVEL)
        self.logger.setLevel(level)
        
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
        #print ("Done init self")
	
    def play_light(self, lightEffect):
        light_pkt ['data']['animation'] = lightEffect
        light_pkt ['data']['path'] = os.getcwd() 
        print(f"Light Effect {lightEffect}  in {light_pkt['data']['path']}" )
        self.publish(LIGHT_TOPIC, json.dumps(light_pkt))
    
    def play_audio(self, file):
        print ("Playing" , file)
        start_audio_pkt ['data']['file'] = file
        start_audio_pkt ['data']['path'] = os.getcwd()
        self.publish(AUDIO_TOPIC, json.dumps(start_audio_pkt))
    
    
    def _kill_game(self):
        # kills current game
        
        print("Killing Process")
        self.child_process.kill()
        self.child_process = None
        self.play_light ('app_stopped.csv')
        self.runningSpell = ""
        

    #Handles button events
    def on_button_press(self, client, userdata, msg):
        payload = json.loads(msg.payload)
        keyPressType = payload['data']['event'] 
        if keyPressType == 'long':
            if self.child_process is not None:
                self._kill_game() 
            else:
                #Long press while idle - what should the behavior be?
                print("Long press while idle")
            

    def _start_game(self, game: str):
        """
        starts game. assumes path is valid per helper.fetch_game checking
        """
        print("Start game called")
        
        filePath = helper.fetch_game(game)
        filePathandMain = filePath + "/main.py"
        
        if filePath is not None:
            print(f"Setting Process args to {filePathandMain} {filePath}")
            self.child_process = subprocess.Popen(['python3', filePathandMain, filePath ] )
            print(f"[SUBPROCESS ID] {self.child_process.pid}")
            
        else:
            print("invalid game found...")

    def on_nfc_scan(self, client, userdata, msg):
        """
        handles logic for starting games
        """
        print("[NFC SCAN] Scan event")
        payload = json.loads(msg.payload)
        
        try:
            if len(payload['card_data']['records']) > 0:
                cardRecord0 = payload_url = payload['card_data']['records'][0]
                
                if cardRecord0 ["data"] == "https://www.thegoodwand.com":
                    print("[NFC SCAN] The Good Wand Card")
                    cardData = payload['card_data']['records'][1]["data"]
                    card_dict = json.loads(cardData)
                    game_on_card = card_dict ["spell"]
                    print (f"[SPELL] {game_on_card}      [RUNNING] {self.runningSpell}")
                    
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
                        print("[NFC SCAN] Spell already running")                
                else:
                        print("[NFC SCAN] NOT a TGW card") 
                        # Add here support for identifying Yoto and starting it
            else:
                print('[NFC SCAN] No records')
        except:
            print('[NFC SCAN] JSON parsing error')

    def run(self):
        #print ("Conductor Running self")
        self.start_mqtt(CONDUCTOR_CLIENT_ID, self.callbacks)
        self.play_light ('power_on.csv')
        #print("Done with init animation")
        signal.pause()


if __name__ == '__main__':
    service = TGWConductor()  
    #print ("starting in __name")
    service.run() 