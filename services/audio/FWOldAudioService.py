#!/usr/bin/env python3
# -*- mode: python; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-

# Simple test script that plays (some) wav files


import wave
import alsaaudio
from paho.mqtt import client as mqtt_client
import json

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
        print(f'msg received: {payload}')
        if payload["data"]["action"] == "START":
            self.file_queue.append(payload['data']["file"])
        else:
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
                # try:
                    print("playing audio")
                    self.play(self.file_queue.pop(0))
                # except:
                #     print("ERROR playing audio")

    def play(self, filename):	
        with wave.open(filename, 'rb') as f:
            format = None
            device = 'default'

            # 8bit is unsigned in wav files
            if f.getsampwidth() == 1:
                format = alsaaudio.PCM_FORMAT_U8
            # Otherwise we assume signed data, little endian
            elif f.getsampwidth() == 2:
                format = alsaaudio.PCM_FORMAT_S16_LE
            elif f.getsampwidth() == 3:
                format = alsaaudio.PCM_FORMAT_S24_3LE
            elif f.getsampwidth() == 4:
                format = alsaaudio.PCM_FORMAT_S32_LE
            else:
                raise ValueError('Unsupported format')

            periodsize = f.getframerate() // 8

            print('%d channels, %d sampling rate, format %d, periodsize %d\n' % (f.getnchannels(),
                                                                                f.getframerate(),
                                                                                format,
                                                                                periodsize))

            device = alsaaudio.PCM(channels=f.getnchannels(), rate=f.getframerate(), format=format, periodsize=periodsize, device=device)
            
            data = f.readframes(periodsize)
            while data:
                # Read data from stdin
                device.write(data)
                if self.stop:
                    data = []
                else:
                    data = f.readframes(periodsize)

if __name__ == '__main__':
    service = FWAudioService()  
    service.run()
