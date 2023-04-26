import time

import sys
import os
sys.path.append(os.path.expanduser('~/templates'))
from MQTTObject import MQTTObject

CALLBACK1_TOPIC = "topic1"
CALLBACK2_TOPIC = "topic2"
PUBLISH_TOPIC = "topic3"
GENERIC_CLIENT_ID = "client"

class GenericMQTTService(MQTTObject):

    def __init__(self):
        super().__init__()

        self.callbacks = {
            CALLBACK1_TOPIC : self.callback1,
            CALLBACK2_TOPIC :  self.callback2
        }

    def callback1(self, client, userdata, msg):
        print('callback 1!')

    def callback2(self, client, userdata, msg):
        print('callback 2!')

    def run(self):
        self.start_mqtt(GENERIC_CLIENT_ID, self.callbacks)
        while True:
            self.publish(PUBLISH_TOPIC, "hello world!")
            print('publishing hello world!')
            time.sleep(3)


if __name__ == '__main__':
    service = GenericMQTTService()  
    service.run() 