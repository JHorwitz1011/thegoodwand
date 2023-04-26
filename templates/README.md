# Templates #

## Abstracts away commonly used processes via template classes.

To use, add repository to system path at the top of a python script:

```python
import sys
import os
sys.path.append(os.path.expanduser('~/templates'))
from MQTTObject import MQTTObject
```

## MQTTObject.py ##
Abstracts away all MQTT bits left with publish and subscribe commands

```python
def start_mqtt(self, client_id: str, topics_and_callbacks: dict) -> None
```

- client_id (str): name of client that is presented to the broker
- topics_and_callbacks (dict): keys of topics, values of callback functions
    - ensure callbacks have format: `callback(self, client, userdata, msg)`
    - assumes valid topic string


```python 
def publish(self, topic: str, payload: str, qos: int = 0) -> None:
```

- topic (str): topic to publish to. assumes valid topic.
- payload (str): data to publish
- qos (int): OPTIONAL quality of service of publish.
    - 0 for send and forget once
    - 1 for guaranteed send at least once potentially more
    - 2 for exactly once with delivery guarantees

Base implementation is as follows:

```python
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
```

