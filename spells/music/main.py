#! /usr/bin/env python3
import time
import json
import sys
import math
import os

from paho.mqtt import client as mqtt_client

# orientation values
# {-1: "unknown", 1: "X-", 2: "X+", 4: "Y-", 8: "Y+", 16: "Z-", 32: "Z+"}     
# are converted using log to number and then mapped to string:
# so 1 = 2^0 = flat button pointing right: 'rit'
# so 2 = 2^1 = flat button pointing left: 'lft'
# so 4 = 2^2 = pointing downward 'pt-dn'
# so 8 = 2^3 = pointing up 'pt-up'
# so 16 = 2^4 = flat button pointing down 'fltdn'
# so 16 = 2^5 = flat button pointing up 'fltup'

#Format for filenames: 
# start with 2SPL
# add -rit -lft -ptdn -ptup flatdn flatup
# then add -drum -horn -triangle -flute
#            
#       
# audio_effects =["2SPL1", "2SPL2","2SPL3","2SPL4","2SPL5","2SPL6"]
orientationText = ["rit","lft","ptdn","ptup","fltdn","fltup"]
instrumentName = 'drum'           

broker = 'localhost'
port = 1883
light_topic = "goodwand/ui/view/lightbar"
audio_topic = "goodwand/ui/view/audio_playback"
gesture_topic = "goodwand/ui/controller/gesture"
nfc_topic = "goodwand/ui/controller/nfc"

# generate client ID with pub prefix randomly
client_id = 'temp-test-client'


start_audio_pkt = {
    "header": {
      "type": "UI_AUDIO", "version": 1
},
    "data": {
     	"action": "START", 
	 	"path": os.getcwd(),
	 	"file": "2SPWelcome.wav"
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
				"path": os.getcwd(),
        		"crossfade": 0
            }
        }


class SpellTwo ():
	global old_orient
	global instrumentName 

	def play_audio(self, client, file):
		print ("Playing" , file)
		start_audio_pkt ['data']['file'] = file
		start_audio_pkt ['data']['path'] = os.getcwd()
		self.publish(client, audio_topic, start_audio_pkt)

	def play_light(self, client, lightEffect):
		light_pkt ['data']['animation'] = lightEffect
		light_pkt ['data']['path'] = os.getcwd() 
		print ("Light Effect" , lightEffect, " in ", light_pkt ['data']['path'] )
		self.publish(client, light_topic, light_pkt)



	def connect_mqtt(self):
		def on_connect(client, userdata, flags, rc): ### FIXED INDENTATION ERROR
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
		global old_orient
		global instrumentName 

		print ("Rcvd Message")
		payload = json.loads(msg.payload)
		msgType = payload['header']['type']
		print ("Rcvd OnMessage with type=" + msgType)

		if msgType == 'UI_NFC':
			for record in payload['card_data']['records']:
				if record['type'] == "text":
					cardData = json.loads(record['data'])
					if cardData['spell']=='music':
						if "instrument" in cardData: 
							instrumentName = cardData['instrument']
							print ('instrumentName set to', instrumentName)

						if 'background' in cardData:
							backTrack = cardData['background']
							fileName = backTrack + '.wav'
							print ("playing in background:", fileName)
							# we should stop the old background music - but thats tricky
							self.play_audio (client, fileName)
						self.play_light (client, 'yes')	

		if msgType == "UI_GESTURE":
			new_orientation =   payload['data']["orientation"]
			new_orient = int(math.log(new_orientation,2))
			print('new orientation is:',new_orient,'/', old_orient)
			fileName = "2SPL" + orientationText[new_orient] + '-' + instrumentName
			print('FileName is:', fileName)
			self.play_audio (client, fileName + '.wav')
			self.play_light (client, fileName + '.csv')	
			old_orient = new_orient 



	def publish(self, client, topic, pkt):
		try:
			result = client.publish(topic, json.dumps(pkt))
			# result: [0, 1]
			status = result[0]
			if status == 0:
				print(f"Publishing Msg")
			else:
				print(f"Failed to send message to topic {topic}")
		except IndexError:
			print("ERROR: no argument given. please use format: python3 pub_client.py [animation code]") ### another......... indent error come on ram :(
	


	def run(self):
		global old_orient
		old_orient = 0
		instrumentName = 'drum'

		client = self.connect_mqtt()
		client.on_message = self.on_message
		client.subscribe(gesture_topic)
		client.subscribe(nfc_topic)
		client.enable_logger()
		print('subscribed!')

		#Play the initial audio and light

		self.play_audio (client, "2SPL2B.wav")
		self.play_light (client, "yipee")

		client.loop_forever()


if __name__ == '__main__':
    service = SpellTwo()
    service.run()
