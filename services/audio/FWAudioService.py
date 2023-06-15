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
import signal

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from log import log

DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)

broker = 'localhost'
port = 1883
audio_topic = "goodwand/ui/view/audio_playback"
client_id = 'TGW-AudioService'



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
        signal.pause()


if __name__ == '__main__':
    service = FWAudioService()
    service.run()
