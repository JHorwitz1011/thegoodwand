#!/usr/bin/env python3

# -*- mode: python; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

# Simple test script that plays (some) wav files


#import wave
#import alsaaudio
from paho.mqtt import client as mqtt_client
import json
import os
import sys
import logging


broker = 'localhost'
port = 1883
audio_topic = "goodwand/ui/view/audio_playback"
client_id = 'TGW-AudioService'

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



class FWAudioService():
    #set constants and the such
    def __init__(self):
        self.file_queue = []
        self.stop = False

    ############### MQTT ###############################
    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.debug(f"Audio Connected to MQTT Broker!")
            else:
                logger.debug(f"Audio Failed to connect to MQTT server, return code {rc}")

        client = mqtt_client.Client(client_id)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client

    def on_message(self, client, userdata, msg):
        payload = json.loads(msg.payload)
        msgCommand = payload["data"]["action"]
        logger.debug (f"Audio command {msgCommand}")
        try:
            playMode = payload["data"]["mode"]
        except:
            playMode =""
            logger.debug (f"No playMode rcvd")

        if  msgCommand == "START":            
            try:
                audioPath = payload['data']["path"]
            except:
                audioPath = ""    

            if audioPath != "":
                fileToPlay = audioPath + "/" + payload['data']["file"]
            else:
                fileToPlay = payload['data']["file"]
                
            logger.info(f'Playing file: {fileToPlay} {playMode}') 

            if playMode == "background":
                logger.debug (f"Background Play")
                os.system("aplay " + fileToPlay + "&")
            else:
                logger.debug (f"Foreground Play")
                os.system("aplay " + fileToPlay)
        else:
            if msgCommand == "STOP":
                logger.debug (f"Stopping all audio")
                os.system("sudo killall aplay") 
            else:
                logger.debug(f"OTHER msg received: {msgCommand}")
                self.stop = True


    ################## MAIN LOOP ##########################
    def run(self):
        client = self.connect_mqtt()
        client.on_message = self.on_message

        client.subscribe(audio_topic)
        client.enable_logger()
        client.loop_start()
        size = 20
        while True:
            if self.file_queue:
                 try:
                    logger.debug (f"playing audio")
                    self.play(self.file_queue.pop(0))
                 except:
                     logger.debug (f"ERROR playing audio")

    def play(self, filename):
	                    logger.debug (f"Popping from queue")
                            #os.system("aplay " + filename)



if __name__ == '__main__':
    service = FWAudioService()
    service.run()
