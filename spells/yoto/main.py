
import subprocess
import requests
import json
import socket
import os
import vlc

from paho.mqtt import client as mqtt_client


broker = 'localhost'
port = 1883
light_topic = "goodwand/ui/view/lightbar"
audio_topic = "goodwand/ui/view/audio_playback"
gesture_topic = "goodwand/ui/controller/gesture"
nfc_topic = "goodwand/ui/controller/nfc"

wandOrient = {"unknown":-1, "X-":1, "X+":2, "Y-":4, "Y+":8, "Z-":16, "Z+":32} 

# generate client ID with pub prefix randomly
client_id = 'temp-test-client'


start_audio_pkt = {
    "header": {
        "type": "UI_AUDIO", "version": 1
    },
    "data": {
        "action": "START",
        "file": "2SPL1.wav",
        "path": ""
    }
}


light_pkt = {
            "header": {
                "type": "UI_LIGHTBAR",
                "version": 1,
            },
            "data": {
                        "granularity": 1,
                        "animation": "yipee",
                "crossfade": 0
            }
        }
player = vlc.Instance()
media_player = player.media_player_new()



class SpellYoto ():

    def play_audio(self, client, file):
        print("Playing", file)
        start_audio_pkt['data']['path'] = os.getcwd() 
        start_audio_pkt['data']['file'] = file
        self.publish(client, audio_topic, start_audio_pkt)

    def playYotoMedia (self,client,cardUrl):
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
        print("Now playing media")
        media_player.play()


    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):  # FIXED INDENTATION ERROR
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(client_id)
        client.on_connect = on_connect
        client.connect(broker, port)
        print("Attempting to connect to MQTT server")
        return client

    def on_message(self, client, userdate, msg):
        msgPayload = json.loads(msg.payload)
        msgType = msgPayload['header']['type']
        print("Rcvd MSG:"+msgType)
        
        if msgType == "UI_GESTURE":
            new_orientation = msgPayload['data']['orientation']
            print('new orientation is:', new_orientation)
            if new_orientation == 32:
                print("PLAY: This is what is should do when newOr==32==horizontal, top up")
                media_player.play()
            if new_orientation == 16:
                print("PAUSE: New Orientation is 16 ==horizontal, top DN ")
                media_player.pause()
            if new_orientation == 2:
                print("Volume Dn: New Orientation is 2 ==sidewaays left")
                media_player.audio_set_volume(50)
            if new_orientation == 1:
                print("Volume Up: New Orientation is 1 ==sidewaays right")
                media_player.audio_set_volume(100)

        if msgType == 'UI_NFC':
            uid = msgPayload['card_data']['uid']
            print ("Rcvd NFC message with payload=" + str(msgPayload))
            cardData = []
            for record in msgPayload['card_data']['records']:  #do what you want with data. 
                if record['type'] == "text":
                    cardData.append(record['data'])
                    print("Record text=",record['data'])

                if record['type'] == "uri":
                    print("Record URL=",record['data'])
                    cardData.append(record['data']) 
            
            print("Going to fetch media for card:",cardData[0] )
            self.playYotoMedia (client, cardData[0])

    def publish(self, client, topic, pkt):
        try:
            result = client.publish(topic, json.dumps(pkt))
            # result: [0, 1]
            status = result[0]
            if status == 0:
                print(f"Publishing MQTT Event")
            else:
                print(f"Failed to send message to topic {topic}")
        except IndexError:
            # another......... indent error come on ram :(
            print(
                "ERROR: no argument given. please use format: python3 pub_client.py [animation code]")

    def run(self):
        global old_orient
        old_orient = 0
        
        # Lets prep the vlc to play audio
       
        

        client = self.connect_mqtt()
        client.on_message = self.on_message
        client.subscribe(gesture_topic)
        client.subscribe(nfc_topic)
        client.enable_logger()
        print('subscribed!')
        self.publish(client, light_topic, light_pkt)
        self.publish(client, audio_topic, start_audio_pkt)
        client.loop_forever()


if __name__ == '__main__':
    service = SpellYoto()
    service.run()
