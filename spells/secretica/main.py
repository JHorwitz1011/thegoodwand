
import time
import signal
import json
import sys, os

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from Services import MQTTClient
from Services import ButtonService
from Services import LightService
from Services import AudioService
from Services import NFCService
from Services import UVService
from log import log

DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)

MQTT_CLIENT_ID = "secretica"

UV_BUTTON_TIME = 8 
UV_NFC_TIME = 15

class Secretica():

    def __init__(self):
        self.currentPath = self.get_path()

        self.mqtt_object = MQTTClient()
        self.mqtt_client = self.mqtt_object.start(MQTT_CLIENT_ID)
        
        self.button = ButtonService(self.mqtt_client)
        self.button.subscribe(self.on_button_press)
        
        self.nfc = NFCService(self.mqtt_client)
        self.nfc.subscribe(self.on_nfc_scan)
        
        self.audio = AudioService(self.mqtt_client, self.currentPath)
        
        self.lights = LightService(self.mqtt_client, self.currentPath)

        self.uv = UVService(self.mqtt_client)


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

    def play_animations(self):
        self.play_audio ("uv_activated.wav", "background")
        self.play_light ("uv_activated.csv")

    def activate_uv(self, on_time):
        uvStartTime = time.strftime("%M:%S +000")
        logger.info (f"Start  activate {uvStartTime}")
        self.uv.on(on_time)

        

    #Handles button events
    def on_button_press(self, keyPressType):   
        if keyPressType == 'short':
            self.activate_uv(UV_BUTTON_TIME)
            self.play_animations()

    def on_nfc_scan(self, payload):
        """
        handles logic for starting games
        """
        secretica = False
        if len(payload['card_data']['records']) > 0:
            cardRecord0 = payload_url = payload['card_data']['records'][0]
            if cardRecord0 ["data"] == "https://www.thegoodwand.com":
                cardRecord1 = payload['card_data']['records'][1]
                cardData = cardRecord1 ["data"]
                card_dict = json.loads(cardData)
                try:
                    game_on_card = card_dict ["spell"]
                    logger.debug (f"spell is: {game_on_card}")
                    # Need to add code that:
                    if game_on_card == "secretica":
                        secretica = True
                        logger.info (f"re activating secretica through NFC")
                        
                    # if the spell=secretica, then turn UV light on for 20 seconds
                    # LED effect of 20 seconds goes from all LEDs to none
                    # Turn off UV Light
                    # play humming audio in the background
                
                except:
                    logger.debug (f"Not a spell")

        else:    
            logger.debug(f'No records found on NFC card')
        
        if secretica:
            self.activate_uv(UV_NFC_TIME) 
            self.play_animations()


    def get_path(self):
        param_1 = None
        if len(sys.argv) < 2:
            logger.debug("No arguments provided.")
        else:
            param_1 = sys.argv[1]
            # Rest of your code using param_1
        return param_1 if param_1 else os.getcwd()
      
    def signal_handler(self, sig, frame): 
        logger.info("Exiting Secretica...")
        self.stop_audio()
        sys.exit(0)  

    def run(self):
        logger.debug(f'Secretica spell started')
    
        logger.debug(f'Secretica spell path is{self.currentPath}')
        self.play_audio ("secretica.wav", "background")
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.pause()


if __name__ == '__main__':
    service = Secretica()  
    service.run() 