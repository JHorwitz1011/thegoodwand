# On card scan, say "activating Yoto" and then start playing teh card content
# Gestures to PAUSE, Rewing to begning of chapter, switch to next chapter
# 
# If another Yoto card is touched whileplaying, jump to this card
#
#
#
#

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
import helper
import requests
import socket
import vlc


sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from MQTTObject import MQTTObject
from paho.mqtt import client as mqtt_client


broker = 'localhost'
port = 1883
NFC_TOPIC = "goodwand/ui/controller/nfc"
BUTTON_TOPIC = "goodwand/ui/controller/button"
GESTURE_TOPIC = "goodwand/ui/controller/gesture"
LIGHT_TOPIC = "goodwand/ui/view/lightbar"
AUDIO_TOPIC = "goodwand/ui/view/audio_playback"
UV_TOPIC = "goodwand/ui/view/uv"

wandOrient = {"unknown":-1, "X-":1, "X+":2, "Y-":4, "Y+":8, "Z-":16, "Z+":32} 

# generate client ID with pub prefix randomly
SPELL_CLIENT_ID = "Yoto"
YOTO_URL = "https://yoto.io/"

# Logger configuration
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

player = vlc.Instance()
media_player = player.media_player_new()


class Yoto (MQTTObject):

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
    

    def playYotoMedia (self,cardUrl):
        # Use the URL from the sample card. later on it should come from the NFC MQTT event
        #cardUrl = 'http://yoto.io/eb9jP?84p7jlsM00p0=zXLJUAWfgktji'
        #cardUrl = "https://yoto.io/h84o2?84iqvisM00p1=cj24XMoeUhNsH"

        # Get the JSON
        print("Requesting JSON for card url:" + cardUrl)
        reqHeaders = {'Accept': 'application/json'}
        response = requests.get(url=cardUrl, headers=reqHeaders)
        print("The Response status code is:" + str(response.status_code))
        print("The card JSON is:" + response.text)
        # Look at the JSON for [card][content][chapters][0][tracks][0][trackUrl]
        resp_dict = response.json()
        mediaUrl = str(resp_dict['card']['content']
               ['chapters'][0]['tracks'][0]['trackUrl'])
        print("The First track url is:" + mediaUrl)

        # Once we get the media URL, setup a CURL command with the HTTP Accept MP$ and redirect content to aplay
        print("Attempting to fetch the media")
        mediaHeaders = {'Content-type': 'video/mp4'}
        response = requests.get(url=mediaUrl, headers=mediaHeaders)
        print("The Media Response status code is:" + str(response.status_code))

        # Now write the media file
        with open("rcvd23.m4a", "wb") as rcvdFile:
            rcvdFile.write(response.content)
            print("Media File Fetched")
        print("Now adding filename to play")
      
        media = player.media_new("rcvd23.m4a")
        print("Now setting media")
        media_player.set_media(media)
        logger.debug(f"Now playing media")
        # Stop any background audio from the start spell
        logger.debug(f"Stopping all background media")
        self.stop_audio ()
        # And start the VLC playing the m4a file we received
        logger.debug(f"Now playing media")
        media_player.play()

    def on_button_press(self, client, userdata, msg):
            payload = json.loads(msg.payload)
            keyPressType = payload['data']['event'] 
            if keyPressType == 'short':
                logger.debug(f"short button pressed while in Yoto")

    def on_gesture(self, client, userdata, msg):    
        global oldOrient
        payload = json.loads(msg.payload)
        newOrientation =   payload['data']["orientation"]
        newOrient = int(math.log(newOrientation,2))

        logger.debug(f'new orientation is: {newOrientation}')
        if newOrientation == 32:
            print("PLAY: This is what is should do when newOr==32==horizontal, top up")
            media_player.play()
        if newOrientation == 16:
            print("PAUSE: New Orientation is 16 ==horizontal, top DN ")
            media_player.pause()
        if newOrientation == 2:
            print("Volume Dn: New Orientation is 2 ==sidewaays left")
            media_player.audio_set_volume(50)
        if newOrientation == 1:
            print("Volume Up: New Orientation is 1 ==sidewaays right")
            media_player.audio_set_volume(100)

    def on_nfc_scan(self, client, userdata, msg):
        """
        handles logic for starting games
        """
        payload = json.loads(msg.payload)
        if len(payload['card_data']['records']) > 0:
            cardUrl = payload['card_data']['records'][0]["data"]
            if cardUrl [0:16] == YOTO_URL:
                logger.debug (f"Yoto reactivated with {cardUrl}")
                cardData = []
                for record in msgPayload['card_data']['records']: 
                    if record['type'] == "text":
                        cardData.append(record['data'])
                        print("Record text=",record['data'])

                    if record['type'] == "uri":
                        print("Record URL=",record['data'])
                        cardData.append(record['data']) 
            
                    print("Going to fetch media for card:",cardData[0] )
                    self.playYotoMedia (client, cardData[0])

            else:
                logger.debug ("not a Yoto card so Conductor should handle")

    def run(self):
        global old_orient
        old_orient = 0
        global currentPath
        logger.debug(f'Yoto spell started')
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

        audio_pkt ['data']['path'] = currentPath
        light_pkt ['data']['path'] = currentPath

        # Lets prep the vlc to play audio
        self.play_audio ("YotoComing.wav","")
        self.play_light ("YotoCountdown.csv")
        self.play_audio ("countdown10-1.wav","background")
        if param_2 != "":
            logger.debug (f"Need to start playing card {YOTO_URL} : {param_2}")
            self.playYotoMedia (YOTO_URL+param_2)
            

        signal.pause()


if __name__ == '__main__':
    service = Yoto()
    service.run()
