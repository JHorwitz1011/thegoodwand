from inspect import isgenerator
import os
from socketserver import ThreadingUnixStreamServer
import sys
import signal
import time
from edge_impulse_linux.runner import ImpulseRunner
import json

# import template file
sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from Services import *
from log import log


DEBUG_LEVEL = "INFO"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)


GESTURE_TEMP_PKT = {
	"header": {
		"type": "UI_GESTURE",
		"version": 1
    },
    "data": None
}

# MQTT constants
GESTURE_TOPIC = "goodwand/ui/controller/gesturerec"
GESTURE_CMD_TOPIC = "goodwand/ui/controller/gesturerec/command"
KEYWORD_CLIENT_ID = "gesture-classifier"

# EI constants
MODEL = "model.eim"
MODEL_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR_PATH, MODEL)

# service constants
GESTURE_THRESHOLD = 0.9 # minimum confidence rating for keyword to publish
ANOMOLY_THRESHOLD = 0.7
MODEL_RATE = 10 # hz

FS = 26 # hz
SAMPLE_LENGTH = 1 # second
NUM_FEATURES = 6
BUFFER_SIZE = SAMPLE_LENGTH * FS * NUM_FEATURES
COOLDOWN = 1


class GestureClassifier():
    def __init__(self):
        self.mqtt_obj = MQTTClient()
        self.mqtt_client = self.mqtt_obj.start("gesture recognition")
        self.imu = IMUService(self.mqtt_client)
        self.imu.subscribe_stream(self.onIMUStream)
        self.imu.enable_stream()
        self.running = True
        self.runner = None                                                                      # ensures runner stops on edge cases
        self.values = BUFFER_SIZE*[0]
        self.last_trigger = 0
        time.sleep(2)

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def onIMUStream(self, msg):
        accel = msg["accel"]
        gyro = msg["gyro"]
        self.values.append(accel['x'])
        self.values.append(accel['y'])
        self.values.append(accel['z'])
        self.values.append(gyro['x'])
        self.values.append(gyro['y'])
        self.values.append(gyro['z'])

        if len(self.values) > BUFFER_SIZE:
            for x in range(6):
                self.values.pop(0)

        logger.debug(f"{time.time()}, {len(self.values)}")

    def signal_handler(self, sig, frame):
        logger.debug(f'Keyword Classifier Interrupted')
        if (self.runner):
            logger.debug(f'Stopping self')
            self.runner.stop()
        self.imu.disable_stream()
        time.sleep(1)
        sys.exit(0)

    def _on_cmd_recv(self, client, userdata, message):
        msg = json.loads(message.payload)
        hdr = msg['header']
        data = msg['data']
        logger.debug(f"\n\nCMD RECEIVED: {message.payload}\n\n")
        if data.get('state') is not None:
            state = data['state']
            
            if state == 0:
                self.running = False
            elif state == 1 and not self.running:
                self.running = True
                logger.debug('starting gesture info')
            elif state == 1:
                logger.debug(f'service already running, ignoring...')

    def run(self):
        while(1):
            if not self.running:
                time.sleep(.03)
            else:
                self.recognize()
                # time.sleep(5)

    def _isAnomaly(self, value):
        return value > ANOMOLY_THRESHOLD
    
    def _isGestureDetected(self, value):
        if value is not None and value >= GESTURE_THRESHOLD:
            return True
        else:
            return False

    def recognize(self):
        self.runner = ImpulseRunner(MODEL_PATH)

        try:
            model_info = self.runner.init()
            print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')

            while True:
                res = self.runner.classify(self.values)
                result = res['result']
                print(res["result"])
                print(self.values)

                classification = result['classification']
                if not self._isAnomaly(classification['unknown']):
                    if self._isGestureDetected(classification['jab']):
                        GESTURE_TEMP_PKT["data"] = {"gesture":"jab"}
                        self.mqtt_client.publish(GESTURE_TOPIC, json.dumps(GESTURE_TEMP_PKT))
                        time.sleep(COOLDOWN)
                        # self.values = BUFFER_SIZE*[0]
                    elif self._isGestureDetected(classification['channel']):
                        GESTURE_TEMP_PKT["data"] = {"gesture":"channel"}
                        self.mqtt_client.publish(GESTURE_TOPIC, json.dumps(GESTURE_TEMP_PKT))
                        time.sleep(COOLDOWN)
                        # self.values = BUFFER_SIZE*[0]
                    elif self._isGestureDetected(classification['flick']):
                        GESTURE_TEMP_PKT["data"] = {"gesture":"flick"}
                        self.mqtt_client.publish(GESTURE_TOPIC, json.dumps(GESTURE_TEMP_PKT))
                        time.sleep(COOLDOWN)
                        # self.values = BUFFER_SIZE*[0]
                time.sleep(1/MODEL_RATE)
        finally:
            if (self.runner):
                self.runner.stop()




if __name__ == '__main__':
    service = GestureClassifier()  
    service.run() 