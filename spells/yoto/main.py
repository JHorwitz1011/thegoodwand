# On card scan, say "activating Yoto" and then start playing teh card content
# Gestures to PAUSE, Rewing to begning of chapter, switch to next chapter
# 
# If another Yoto card is touched whileplaying, jump to this card

import signal
import json
import sys
import os
import logging
import math
import requests
import vlc

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from Services import *
from log import log

DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name=LOGGER_NAME, level=DEBUG_LEVEL)

wandOrient = {"unknown":-1, "X-":1, "X+":2, "Y-":4, "Y+":8, "Z-":16, "Z+":32} 

# generate client ID with pub prefix randomly
MQTT_CLIENT_ID = "Yoto"
YOTO_URL = "https://yoto.io/"

player = vlc.Instance()
media_player = player.media_player_new()


class Yoto ():

    def __init__(self):
        
        self.currentPath = self.get_path()
        
        self.mqtt_object = MQTTClient()
        self.mqtt_client = self.mqtt_object.start(MQTT_CLIENT_ID)
        
        self.button = ButtonService(self.mqtt_client)
        self.button.subscribe(self.on_button_press)
        
        #NFC not used as of now. 
        self.nfc = NFCService(self.mqtt_client)
        self.nfc.subscribe(self.on_nfc_scan)
        
        self.imu = IMUService(self.mqtt_client)
        self.imu.subscribe_orientation(self.on_gesture)

        self.audio = AudioService(self.mqtt_client, self.currentPath)
        
        self.lights = LightService(self.mqtt_client, self.currentPath) 

        self.old_orient = 0       
        

    def play_audio(self, file, playMode):
        logger.info(f"Play audio file {file}")
        
        if playMode == "background": 
            self.audio.play_background(file)
        elif playMode == "foreground":
            self.audio.play_foreground(file)
        else:
            logger.warning(f"unknown play mode {playMode}")


    def stop_audio(self):
        logger.info(f"[Audio] stop all")
        self.audio.stop()


    def play_light(self, lightEffect):
        logger.info(f"Light Effect {lightEffect}")
        self.lights.play_lb_csv_animation(lightEffect)
    

    def fetch_yoto(self, cardUrl):
        # Get the JSON
        logger.debug(f"Requesting JSON for card url: {cardUrl}")

        reqHeaders = {'Accept': 'application/json'}
        response = requests.get(url=cardUrl, headers=reqHeaders)

        logger.debug(f"The card JSON is: {response.text}")
 
        if response.status_code != 200:
            logger.debug(f"Failed to get card data: {response.status_code}")
            #return None
        else: 
            logger.debug(f"get card data success : {response.status_code}")
    
        # Look at the JSON for [card][content][chapters][0][tracks][0][trackUrl]
        
        resp_dict = response.json()
        mediaUrl = str(resp_dict['card']['content']
               ['chapters'][0]['tracks'][0]['trackUrl'])
        logger.debug("The First track url is:" + mediaUrl)

        # Once we get the media URL, setup a CURL command with the 
        # HTTP Accept MP$ and redirect content to aplay
        mediaHeaders = {'Content-type': 'video/mp4'}
        response = requests.get(url=mediaUrl, headers=mediaHeaders)
        
        if response.status_code != 200:
            logger.debug(f"Faild to fetch Media:{response.status_code}")
            #return None
        else: 
            logger.debug(f"Fetched Yoto Media:{response.status_code}")

        return response

    # TODO play an error animation so the users know something whent wrong.
    def play_error(self):
        logger.debug("Play Error animations")

    def play_yoto(self, cardUrl):
        # Use the URL from the sample card. later on it should come from the NFC MQTT event
        #cardUrl = 'http://yoto.io/eb9jP?84p7jlsM00p0=zXLJUAWfgktji'
        #cardUrl = "https://yoto.io/h84o2?84iqvisM00p1=cj24XMoeUhNsH"
        self.play_animations()
        response = self.fetch_yoto(cardUrl)
        # And error occured fetching the data. 
        if response == None:
            self.play_error()
            return None
        # Now write the media file
        with open("rcvd23.m4a", "wb") as rcvdFile:
            rcvdFile.write(response.content)
            logger.debug("Media File Fetched")
      
        media = player.media_new("rcvd23.m4a")
        media_player.set_media(media)
        # Stop any background audio from the start spell
        logger.debug("Stopping all background media")
        self.stop_audio ()
        # And start the VLC playing the m4a file we received
        logger.debug("Now playing media")
        media_player.play()

    def on_button_press(self,  keyPressType):
        if keyPressType == 'short':
            logger.debug("short button pressed while in Yoto")

    def on_gesture(self, orientation):    

        logger.debug(f'new orientation is: {orientation}')
        if orientation == 32:
            logger.debug("PLAY: This is what is should do when newOr==32==horizontal, top up")
            media_player.play()
        if orientation == 16:
            logger.debug("PAUSE: New Orientation is 16 ==horizontal, top DN ")
            media_player.pause()
        if orientation == 2:
            logger.debug("Volume Dn: New Orientation is 2 ==sidewaays left")
            media_player.audio_set_volume(50)
        if orientation == 1:
            logger.debug("Volume Up: New Orientation is 1 ==sidewaays right")
            media_player.audio_set_volume(100)

    def on_nfc_scan(self, payload):
        """
        handles logic for starting games
        """
        if len(payload['card_data']['records']) > 0:
            cardUrl = payload['card_data']['records'][0]["data"]
        if cardUrl [0:16] == YOTO_URL:
            logger.debug (f"Yoto NFC Card with URL: {cardUrl}")
            self.play_yoto (cardUrl)

        else:
            logger.debug ("not a Yoto card.")

    def get_path(self):
        param_1 = None
        if len(sys.argv) < 2:
            logger.debug("No arguments provided.")
        else:
            param_1 = sys.argv[1]
            # Rest of your code using param_1
        return param_1 if param_1 else os.getcwd()
    
    def get_yoto_card_args(self):
        param_2 = None
        try:
            param_2 = sys.argv[2]
            logger.debug(f"Yoto Arg {param_2}")
        except Exception as e:
            logger.error(f"no args {e}")      

        return param_2

    def signal_handler(self, sig, frame): 
        logger.info("Exiting Yoto...")
        self.stop_audio()
        sys.exit(0)

    def play_animations(self):
        self.play_audio ("YotoComing.wav","forground")
        self.play_light ("YotoCountdown.csv")
        self.play_audio ("countdown10-1.wav","background")

    def run(self):
        logger.debug(f'Yoto spell started')
               
        yoto = self.get_yoto_card_args()

        if yoto:
            logger.debug (f"Need to start playing card {YOTO_URL} : {yoto}")
            self.play_yoto (YOTO_URL+yoto)
        else:
            #TODO indicate to scan card. 
            self.play_error()
            logger.warning("Yoto card not found")
            
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.pause()


if __name__ == '__main__':
    service = Yoto()
    service.run()
