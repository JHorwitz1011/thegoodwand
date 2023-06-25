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
KEYWORD_THRESHOLD = 0.8 # minimum confidence rating for keyword to publish

class TGWKeywordClassifier(MQTTObject):
    def __init__(self, fs=10):
        super().__init__()

        self.active = threading.Event()                                                         # thread based boolean (defaults false thus service is paused on startup)
        self.exit = threading.Event()                                                           # exit var to leave execution (default false)
        self.runner = None                                                                      # ensures runner stops on edge cases
        signal.signal(signal.SIGINT, self.signal_handler)
        self.fs = fs                                                                            
        self.keyword_thread = threading.Thread(target=self.recognize, args=(self.active,))       
        self.topics_and_callbacks = {
            KEYWORD_CMD_TOPIC : self._on_cmd_recv
        }

    
    def signal_handler(self, sig, frame):
        logger.debug(f'Keyword Classifier Interrupted')
        self.active.set()
        self.exit.set()
        self.keyword_thread.join()
        if (self.runner):
            logger.debug(f'Stopping self')
            self.runner.stop()
        sys.exit(0)

    def _on_cmd_recv(self, client, userdata, message):
        msg = json.loads(message.payload)
        hdr = msg['header']
        data = msg['data']
            
        if data.get('state') is not None:
            state = data['state']
            
            if state == 0:
                self.active.clear()
                logger.debug(f"rcvd Cmd to stop voicerec")

            elif state == 1:
                self.active.set()
                logger.debug(f"rcvd Cmd to start voicerec")

    def run(self):
        self.start_mqtt(KEYWORD_CLIENT_ID,self.topics_and_callbacks)
        self.keyword_thread.start()
        
    def recognize(self, event):
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
                        logger.debug(f"recognized colos")
                    elif result["extivious"] > KEYWORD_THRESHOLD:
                        KEYWORD_TEMP_PKT["data"] = {"keyword":"extivious"}
                        self.publish(KEYWORD_TOPIC, json.dumps(KEYWORD_TEMP_PKT))
                        logger.debug(f"recognized extivious")
                    elif result["lumos"] > KEYWORD_THRESHOLD:
                        KEYWORD_TEMP_PKT["data"] = {"keyword":"lumos"}
                        self.publish(KEYWORD_TOPIC, json.dumps(KEYWORD_TEMP_PKT))
                        logger.debug(f"recognized lumos")
                    elif result["mousike"] > KEYWORD_THRESHOLD:
                        KEYWORD_TEMP_PKT["data"] = {"keyword":"mousike"}
                        self.publish(KEYWORD_TOPIC, json.dumps(KEYWORD_TEMP_PKT))
                        logger.debug(f"recognized mousike")
                    # else:
                        # logger.debug(f"{result}")
                    
                    if not self.active.is_set():
                        logger.debug(f'model execution PAUSE')
                        event.wait()
                        logger.debug(f"model execution RESUME")
                    if self.exit.is_set():
                        logger.debug(f"model execution Breaking!")
                        break
                        

                    time.sleep(1/self.fs)
            
            #logger.debug(f"Out of recognize forever loop")
            
            finally:
                if (self.runner):
                    logger.debug(f"finally stopping execution")
                    self.runner.stop()




if __name__ == '__main__':
    service = TGWKeywordClassifier()  
    service.run() 