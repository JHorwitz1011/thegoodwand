import os
import sys
import signal
import time
from edge_impulse_linux.audio import AudioImpulseRunner
import json

# import template file
sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from MQTTObject import MQTTObject

# ensure everything stops on edge case
runner = None
def signal_handler(sig, frame):
    print('Interrupted')
    if (runner):
        runner.stop()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

KEYWORD_TEMP_PKT = {
	"header": {
		"type": "UI_KEYWORD",
		"version": 1
},
    "data": None
}


# MQTT constants
KEYWORD_TOPIC = "goodwand/ui/controller/keyword"
KEYWORD_CLIENT_ID = "keyword-classifier"

# EI constants
MODEL = "modelfile.eim"
MODEL_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR_PATH, MODEL)
AUDIO_DEVICE_ID = 0

class TGWKeywordClassifier(MQTTObject):

    def __init__(self, fs=10):
        super().__init__()
        self.fs = fs

    def run(self):
        self.start_mqtt(KEYWORD_CLIENT_ID)

        with AudioImpulseRunner(MODEL_PATH) as runner:
            try:
                model_info = runner.init()
                print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')                
                print("Device ID "+ str(AUDIO_DEVICE_ID) + " has been provided as an argument.")

                for res, audio in runner.classifier(device_id=AUDIO_DEVICE_ID): # loops forever
                    KEYWORD_TEMP_PKT['data'] = res['result']['classification']
                    self.publish(KEYWORD_TOPIC, json.dumps(KEYWORD_TEMP_PKT))
                    time.sleep(1/self.fs)

            finally:
                if (runner):
                    runner.stop()




if __name__ == '__main__':
    service = TGWKeywordClassifier()  
    service.run() 