#!/usr/bin/env python3

# -*- mode: python; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

# Simple test script that plays (some) wav files


#import wave
#import alsaaudio
from paho.mqtt import client as mqtt_client
import json
import os
import sys


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
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect to MQTT server, return code %d\n", rc)

        client = mqtt_client.Client(client_id)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client

    def on_message(self, client, userdata, msg):
        payload = json.loads(msg.payload)
        
        if payload["data"]["action"] == "START":
            print('START msg received')
            
            try:
                audioPath = payload['data']["path"]
            except:
                audioPath = ""    

            if audioPath != "":
                fileToPlay = audioPath + "/" + payload['data']["file"]
            else:
                fileToPlay = payload['data']["file"]
            print('Playing file:'+ fileToPlay) 
            os.system("aplay " + fileToPlay)
        else:
            print('OTHER? msg received. self.STOP')
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
                    print("playing audio")
                    self.play(self.file_queue.pop(0))
                 except:
                     print("ERROR playing audio")

    def play(self, filename):
	                    print("Popping from queue")
                            #os.system("aplay " + filename)



if __name__ == '__main__':
    service = FWAudioService()
    service.run()
