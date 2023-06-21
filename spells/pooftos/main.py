import signal
import json
import sys, os
import math

# Import TGW libs
sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from Services import *
from log import log

DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name=LOGGER_NAME, level=DEBUG_LEVEL)

MQTT_CLIENT_ID = "pooftos"

class Pooftos():
    oldOrient : int 

    def __init__(self):
        self.currentPath = self.get_path()
        self.mqtt_object = MQTTClient()
        self.mqtt_client = self.mqtt_object.start(MQTT_CLIENT_ID)
        
        self.button = ButtonService(self.mqtt_client)
        self.button.subscribe(self.on_button_press)
        
        # NFC not used as of now. 
        # self.nfc = NFCService(self.mqtt_client)
        # self.nfc.subscribe(self.on_nfc_scan)
        
        self.imu = IMUService(self.mqtt_client)
        self.imu.subscribe_orientation(self.on_gesture)

        self.audio = AudioService(self.mqtt_client, self.currentPath)
        
        self.lights = LightService(self.mqtt_client, self.currentPath)


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


    def deactivate_tv(self):
        self.play_audio("deactive.wav", "background")
        self.play_light("deactive.csv")
        os.system("sh "+ self.currentPath + "/Pooftos.sh " + self.currentPath)

    # Handles Gesture events
    def on_gesture(self, msg):
        newOrientation = msg
        newOrient = int(math.log(newOrientation, 2))
        logger.debug(f"{newOrientation}  {newOrient}")

        if (newOrient == 5) and (self.oldOrient == 3):  # 5=flt-up
            self.deactivate_tv()

        self.oldOrient = newOrient

    def on_button_press(self, keyPressType):
        if keyPressType == 'short':
            self.deactivate_tv()

    # def on_nfc_scan(self, msg):
    #     """
    #     handles logic for starting games
    #     """
    #     payload = json.loads(msg.payload)
    #     if len(payload['card_data']['records']) > 0:
    #         cardRecord0 = payload_url = payload['card_data']['records'][0]
    #         if cardRecord0["data"] == "https://www.thegoodwand.com":
    #             cardRecord1 = payload['card_data']['records'][1]
    #             cardData = cardRecord1["data"]
    #             card_dict = json.loads(cardData)
    #             try:
    #                 game_on_card = card_dict["spell"]
    #                 logger.debug(f"spell is: {game_on_card}")
    #                 # Need to add code that:
    #                 if game_on_card == "pooftos":
    #                     logger.info(f"re activating pooftos through NFC")
    #                     # What should we do here

    #             except:
    #                 logger.debug(f"Not a spell")

    #     else:
    #         logger.debug(f'No records found on NFC card')

    def get_path(self):
        param_1 = None
        if len(sys.argv) < 2:
            logger.debug("No arguments provided.")
        else:
            param_1 = sys.argv[1]
            # Rest of your code using param_1
        return param_1 if param_1 else os.getcwd()

    def signal_handler(self, sig, frame): 
        logger.info("Exiting Pooftos...")
        self.stop_audio()
        sys.exit(0)

    def run(self):
        logger.debug(f'Pooftos spell started')
        self.play_audio("activating-pooftos.wav", "background")
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.pause()

if __name__ == '__main__':
    service = Pooftos()
    service.run()
