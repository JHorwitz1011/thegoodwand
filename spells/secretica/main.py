
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
UV_TOPIC = "goodwand/ui/view/uv"

SPELL_CLIENT_ID = "Secretica"

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

uv_pkt = {
            "header": {"type": "UI_UV","version": 1},
            "data": {
                "state": False,
            }
        }

class Secretica(MQTTObject):

    def __init__(self):
        super().__init__()

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
    
    def set_uv(self, uvStatus):
        print ("Setting up UV to:" , uvStatus)
        uv_pkt ['status'] = uvStatus
        self.publish(UV_TOPIC, json.dumps(uv_pkt))

    #Handles button events
    def on_button_press(self, client, userdata, msg):
        payload = json.loads(msg.payload)
        keyPressType = payload['data']['event'] 
        
        if keyPressType == 'short':
            print ("What should we do with short press")
            


    def on_nfc_scan(self, client, userdata, msg):
        """
        handles logic for starting games
        """
        payload = json.loads(msg.payload)
        if len(payload['card_data']['records']) > 0:
            cardRecord0 = payload_url = payload['card_data']['records'][0]
            if cardRecord0 ["data"] == "https://www.thegoodwand.com":
                print ("One of our cards")
                cardRecord1 = payload['card_data']['records'][1]
                cardData = cardRecord1 ["data"]
                card_dict = json.loads(cardData)
                
                try
                    game_on_card = card_dict ["spell"]
                    print ("spell is:",game_on_card )
                    # Need to add code that:
                    # if the spell=secretica, then turn UV light on for 20 seconds
                    # LED effect of 20 seconds goes from all LEDs to none
                    # Turn off UV Light
                    # play humming audio in the background
                
                
                except
                    print ("Not a spell")

        else:    
            print('No records found')

    def run(self):
        self.start_mqtt(SPELL_CLIENT_ID, self.callbacks)
        self.play_light ('SCR_activated.csv')
        signal.pause()


if __name__ == '__main__':
    service = Secretica()  
    service.run() 