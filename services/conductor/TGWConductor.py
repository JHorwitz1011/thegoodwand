
import time
import signal
import json
from multiprocessing import Process
import subprocess

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
                "animation": "",
				"path": os.getcwd(),
        		"crossfade": 0
            }
        }


#maximum allowed time a button event can register upon nfc tag scan
MAX_BUTTON_LAG = .5 # seconds

runningSpell = "" 

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

        self.child_process = None
        self.time_since_short_press = time.time()
        self.time_since_long_press = time.time()
        self.current_game = ""
        self.client = None

        self.callbacks = {
            NFC_TOPIC : self.on_nfc_scan,
            BUTTON_TOPIC: self.on_button_press,
        }

        	


    def play_light(self, lightEffect):
        light_pkt ['data']['animation'] = lightEffect
        light_pkt ['data']['path'] = os.getcwd() 
        print ("Light Effect" , lightEffect, " in ", light_pkt ['data']['path'] )
        self.publish(LIGHT_TOPIC, json.dumps(light_pkt))
    
    def play_audio(self, file):
        print ("Playing" , file)
        start_audio_pkt ['data']['file'] = file
        start_audio_pkt ['data']['path'] = os.getcwd()
        self.publish(AUDIO_TOPIC, json.dumps(start_audio_pkt))
    
    

    def _kill_game(self):
        # kills current game
        self.child_process.kill()
        self.child_process = None
        print('process killed!')


    def _start_process(self, path_to_main):
        """
        runs python file located at filepath
        """
        print('starting..', path_to_main)
        subprocess.run(['python3', path_to_main])

    #Handles button events
    def on_button_press(self, client, userdata, msg):
        payload = json.loads(msg.payload)
        keyPressType = payload['data']['event'] 
        
        if keyPressType == 'long':
            if self.child_process is not None:
                self._kill_game() 
            else:
                #Long press while idle - what should the behavior be?
                print ("Long press while idle")
            

    def _start_game(self, game: str):
        """
        starts game. assumes path is valid per helper.fetch_game checking
        """
        filepath = helper.fetch_game(game)
        print("Checking for game path=",filepath)
        if filepath is not None:
            self.child_process = Process(target=self._start_process,args=[filepath]) 
            try:
                self.child_process.start()
            except Exception as e:
                print('unable to start process... error:', e)
                self.child_process = None
        else:
            print("invalid game found...")

    def on_nfc_scan(self, client, userdata, msg):
        """
        handles logic for starting games
        """
        global runningSpell
        payload = json.loads(msg.payload)
        try:
            if len(payload['card_data']['records']) > 0:
                cardRecord0 = payload_url = payload['card_data']['records'][0]
                if cardRecord0 ["data"] == "https://www.thegoodwand.com":
                    print ("One of our cards")
                    cardRecord1 = payload['card_data']['records'][1]
                    cardData = cardRecord1 ["data"]
                    card_dict = json.loads(cardData)
                    game_on_card = card_dict ["spell"]
                    print ("spell is:",game_on_card, " and running spell is ",runningSpell)
                    if runningSpell != game_on_card:
                        # This is a different spell, so start it:
                        if self.child_process is None: #no game is running so just start new game
                            self._start_game(game_on_card)
                        else:
                            # Stop currently running game
                            self._kill_game ()
                            self._start_game(game_on_card)                        

                        # Update runningSpell. NOT HANDLING edge condition of spells failing to start
                        runningSpell = game_on_card
                    else:  
                        print ("same as running game, doing nothing")                
                else:
                        print("NOT a TGW card") 
                        # Add here support for identifying Yoto and starting it
            else:
                print('no records found')
        except:
            print("ERROR parsing NFC card")

    def run(self):
        self.start_mqtt(CONDUCTOR_CLIENT_ID, self.callbacks)
        self.play_light ('power_up')
        signal.pause()


if __name__ == '__main__':
    service = TGWConductor()  
    service.run() 