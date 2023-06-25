import os
from socketserver import ThreadingUnixStreamServer
import sys
import signal
import time
from edge_impulse_linux.audio import AudioImpulseRunner
import json
import threading

# import template file
sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from MQTTObject import MQTTObject

from log import log


DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)


KEYWORD_TEMP_PKT = {
	"header": {
		"type": "UI_KEYWORD",
		"version": 1
},
    "data": None
}

# MQTT constants
KEYWORD_TOPIC = "goodwand/ui/controller/keyword"
KEYWORD_CMD_TOPIC = "goodwand/ui/controller/keyword/command"
KEYWORD_CLIENT_ID = "keyword-classifier"

# EI constants
MODEL = "model.eim"
MODEL_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR_PATH, MODEL)
AUDIO_DEVICE_ID = 0 # seeed studio device

# service constants
KEYWORD_THRESHOLD = 0.4 # minimum confidence rating for keyword to publish

class TGWKeywordClassifier(MQTTObject):
    def __init__(self):
        super().__init__()

        self.running = False
        self.runner = None                                                                      # ensures runner stops on edge cases
        signal.signal(signal.SIGINT, self.signal_handler)
        self.topics_and_callbacks = {
            KEYWORD_CMD_TOPIC : self._on_cmd_recv
        }

    
    def signal_handler(self, sig, frame):
        logger.debug(f'Keyword Classifier Interrupted')
        if (self.runner):
            logger.debug(f'Stopping self')
            self.runner.stop()
        sys.exit(0)

    def _on_cmd_recv(self, client, userdata, message):
        msg = json.loads(message.payload)
        hdr = msg['header']
        data = msg['data']
        logger.debug("\n\nCMD RECEIVED: {message.payload}\n\n")
        if data.get('state') is not None:
            state = data['state']
            
            if state == 0:
                self.running = False
            elif state == 1 and not self.running:
                self.running = True
                logger.debug('starting keyword info')
                self.recognize()
            elif state == 1:
                logger.debug(f'service already running, ignoring...')

    def run(self):
        self.start_mqtt_blocking(KEYWORD_CLIENT_ID,self.topics_and_callbacks)
        
    def recognize(self):
        with AudioImpulseRunner(MODEL_PATH) as self.runner:
            try:
                model_info = self.runner.init()
                logger.debug(f'Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')                
                #logger.debug(f"Device ID "+ str(AUDIO_DEVICE_ID) + " has been provided as an argument.")

                for res, audio in self.runner.classifier(device_id=AUDIO_DEVICE_ID): # loops forever
                    result = res['result']['classification']
                    
                    logger.debug(f"rcvd classification event with Lumos: {result['''lumos''']} Extvs: {result['''extivious''']}  colos: {result['''colos''']} mousike: {result['''mousike''']}   ")

                    if result["colos"] > KEYWORD_THRESHOLD:
                        KEYWORD_TEMP_PKT["data"] = {"keyword":"colos"}
                        self.publish(KEYWORD_TOPIC, json.dumps(KEYWORD_TEMP_PKT))
                        logger.debug(f"\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!recognized colos!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
                    elif result["extivious"] > KEYWORD_THRESHOLD:
                        KEYWORD_TEMP_PKT["data"] = {"keyword":"extivious"}
                        self.publish(KEYWORD_TOPIC, json.dumps(KEYWORD_TEMP_PKT))
                        logger.debug(f"\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!recognized extivious!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
                    elif result["lumos"] > KEYWORD_THRESHOLD:
                        KEYWORD_TEMP_PKT["data"] = {"keyword":"lumos"}
                        self.publish(KEYWORD_TOPIC, json.dumps(KEYWORD_TEMP_PKT))
                        logger.debug(f"\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!recognized lumos!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
                    elif result["mousike"] > KEYWORD_THRESHOLD:
                        KEYWORD_TEMP_PKT["data"] = {"keyword":"mousike"}
                        self.publish(KEYWORD_TOPIC, json.dumps(KEYWORD_TEMP_PKT))
                        logger.debug(f"\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!recognized mousike!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
                    else:
                        logger.debug(f"{result}")
                    
                    if not self.running:
                        break
                        
            finally:
                if (self.runner):
                    logger.debug(f"exeting...")
                    self.runner.stop()




if __name__ == '__main__':
    service = TGWKeywordClassifier()  
    service.run() 