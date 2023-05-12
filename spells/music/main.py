#! /usr/bin/env python3
import time
import json
import sys
import math
import os
import logging 
from paho.mqtt import client as mqtt_client

## Logger configuration
## Change level by changing DEBUG_LEVEL variable to ["DEBUG", "INFO", "WARNING", "ERROR"]

DEBUG_LEVEL = "DEBUG" #
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
client_id = 'musicSpell'
#client_id = 'musicSpell' + str(time.time())

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
            "header": {
                "type": "UI_LIGHTBAR",
                "version": 1,
            },
            "data": {
                "granularity": 1,
                "animation": "",
				"path": "" ,
        		"crossfade": 0
            }
        }


class musicSpell():
	global old_orient
	global instrumentName 

	def play_audio(self, client, file, playMode):
		global currentPath
		logger.info(f"Play audio file {file}")
		audio_pkt ['data']['action'] = "START"
		audio_pkt ['data']['file'] = file
		audio_pkt ["data"]["mode"] = playMode 
		self.publish(client, audio_topic, audio_pkt)

	def stop_audio(self, client):
		logger.info(f"[Audio] stop all")
		audio_pkt ['data']['action'] = "STOP"
		self.publish(client, audio_topic, audio_pkt)

	def play_light(self, client, lightEffect):
		light_pkt ['data']['animation'] = lightEffect
		logger.info(f"Light Effect" , lightEffect, " in ", light_pkt ['data']['path'] )
		self.publish(client, light_topic, light_pkt)



	def connect_mqtt(self):
		def on_connect(client, userdata, flags, rc): ### FIXED INDENTATION ERROR
			if rc == 0:
				logger.debug(f"Music Spell Connected to MQTT Broker! PID= {os.getpid()}")
			else:
				logger.warning(f"Music Spell Failed to connect, return code {rc}")
		client = mqtt_client.Client(client_id)
		client.on_connect = on_connect
		client.connect(broker, port)
		logger.debug(f"Connecting to mqtt server...")
		
		return client

	def on_message(self, client, userdate, msg):
		global old_orient
		global instrumentName 

		logger.debug (f"MQTT Message from: {msg.topic}")
		
		try:
			payload = json.loads(msg.payload)
			msgType = payload['header']['type']
			logger.debug(f"MQTT message type: {msgType}")

			if msgType == 'UI_NFC':
				for record in payload['card_data']['records']:
					if record['type'] == "text":
						cardData = json.loads(record['data'])
						if cardData['spell']=='music':

							if "instrument" in cardData: 
								instrumentName = cardData['instrument']
								logger.info(f"instrumentName set to {instrumentName}")

							if 'background' in cardData:
								backTrack = cardData['background']
								fileName = backTrack + '.wav'
								logger.info(f"playing in background: {fileName}")
								# we should stop the old background music - but thats tricky
								self.stop_audio (client)
								self.play_audio (client, fileName, "background")
							
							self.play_light (client, 'yes')	

			if msgType == "UI_GESTURE":
				new_orientation =   payload['data']["orientation"]
				new_orient = int(math.log(new_orientation,2))
				logger.debug(f"orientation change. New: {new_orient}  Old: {old_orient}")
				fileName = "2SPL" + orientationText[new_orient] + '-' + instrumentName
				logger.debug(f"FileName is: {fileName}")
				self.play_audio (client, fileName + '.wav', "foreground")
				self.play_light (client, fileName + '.csv')	
				old_orient = new_orient 
		
		except Exception as e:
			logger.warning(f"JSON parsing excetion {e}")


	def publish(self, client, topic, pkt):
		try:
			result = client.publish(topic, json.dumps(pkt))
			# result: [0, 1]
			status = result[0]
			if status == 0:
				logger.debug(f"published message: {topic}")
			else:
				logger.error(f"Failed to send message to topic {topic}")
		except IndexError:
			logger.warning("no argument given. please use format: python3 pub_client.py [animation code]")
	

	def run(self):
		global old_orient
		global currentPath
		old_orient = 0
		instrumentName = 'drum'
		client = self.connect_mqtt()
		client.on_message = self.on_message
		client.subscribe(gesture_topic)
		client.subscribe(nfc_topic)
		client.enable_logger()
		logger.debug('Music spell subscribed to mqtt!')
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
		logger.info(f"Setting path to: {currentPath}")	
		audio_pkt ['data']['path'] = currentPath
		light_pkt ['data']['path'] = currentPath
		

		# Need to put here code to arse the second argument which is a JSON f
		# from the conductor with the startup info on the card

		#Play the initial audio and light

		#The spell plays audio of its own name
		self.play_audio (client, "music.wav", "background")
		#But Dont play light - conductor plays spell startr light
		
		client.loop_forever()


if __name__ == '__main__':
	service = musicSpell()
	logger.info(f"Music spell running")
	service.run()
