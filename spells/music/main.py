#! /usr/bin/env python3
import time
import json
import sys, os
import math
import signal

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from Services import *
from log import log

DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)

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
           
MQTT_CLIENT_ID = 'musicSpell'


class musicSpell():
	
	old_orient = 0
	
	def __init__(self) -> None:
		self.currentPath = self.get_path()

		self.mqtt_object = MQTTClient()
		self.mqtt_client = self.mqtt_object.start(MQTT_CLIENT_ID)

		# self.button = ButtonService(self.mqtt_client)
		# self.button.subscribe(self.on_button_press)

		self.nfc = NFCService(self.mqtt_client)
		self.nfc.subscribe(self.on_nfc_scan)

		self.imu = IMUService(self.mqtt_client)
		self.imu.subscribe_orientation(self.on_gesture)

		self.audio = AudioService(self.mqtt_client, self.currentPath)

		self.lights = LightService(self.mqtt_client, self.currentPath)

		self.instrumentName = 'drum'		

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
		self.lights.lb_csv_animation(lightEffect)

	def on_nfc_scan(self, payload):

		logger.debug (f"NFC Payload: {payload}")
		
		try:
			for record in payload['card_data']['records']:
				if record['type'] == "text":
					cardData = json.loads(record['data'])
					if cardData['spell']=='music':
						if "instrument" in cardData: 
							self.instrumentName = cardData['instrument']
							logger.info(f"instrumentName set to {self.instrumentName}")

						if 'background' in cardData:
							backTrack = cardData['background']
							fileName = backTrack + '.wav'
							logger.info(f"playing in background: {fileName}")
							# we should stop the old background music - but thats tricky
							self.stop_audio ()
							self.play_audio (fileName, "background")
						
						self.play_light ('yes')	

		except Exception as e:
			logger.warning(f"JSON parsing excetion {e}")

	def on_gesture(self, orientaion):
		new_orientation =  orientaion
		new_orient = int(math.log(new_orientation,2))
		logger.debug(f"orientation change. New: {new_orient}  Old: {self.old_orient}")
		fileName = "2SPL" + orientationText[new_orient] + '-' + self.instrumentName
		logger.debug(f"FileName is: {fileName}")
		self.play_audio (fileName + '.wav', "background")
		self.play_light (fileName + '.csv')	
		self.old_orient = new_orient 

	def get_path(self):
		param_1 = None
		if len(sys.argv) < 2:
			logger.debug("No arguments provided.")
		else:
			param_1 = sys.argv[1]
			# Rest of your code using param_1
		return param_1 if param_1 else os.getcwd()
    
	def signal_handler(self, sig, frame): 
		logger.info("Exiting Music...")
		self.stop_audio()
		sys.exit(0)

	def run(self):
		logger.info(f"Starting Music {self.instrumentName}")	
		# Need to put here code to arse the second argument which is a JSON f
		# from the conductor with the startup info on the card
		#Play the initial audio and light

		#The spell plays audio of its own name
		self.play_audio ("music.wav", "background")
		#But Dont play light - conductor plays spell startr light
		signal.signal(signal.SIGINT, self.signal_handler)
		signal.signal(signal.SIGTERM, self.signal_handler)
		signal.pause()

		

if __name__ == '__main__':
	service = musicSpell()
	service.run()
