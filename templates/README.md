[<- back to home](../README.md)

# IMPORTING TEMPLATES #

To use, add repository to system path at the top of a python script:

```python
import sys
import os
sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
## Used for writing services 
from MQTTObject import MQTTObject
## Only import services needed
## Used by spells and Services to import funticionality from other services 
from Services import IMUService
from Services import NFCService
from Services import AudioService
from Services import LightService
from Services import ButtonService
from Services import MQTTClient

```

# MQTTObject.py #
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
sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
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


# Services.py #

Abstracts away all MQTT bits and gives a common API to be used for all the TWG services. 

Examples can be found in the templates/examples/test_service.py file

## Services Implimented ##
* Lights
* Audio 
* NFC 
* IMU
* Button 

## How to Use ##

* Import the template file. 
* Get an instance of the MQTT client.
* Initialize Service 
* Invoke service functionality 


### MQTT CLIENT ###
```python 
MQTT_CLIENT_ID = "unit_test"

# Initialize the MQTT Client
# @param broker: MQTT Broker ip, default = localhost
# @param port: Port number to be used, default 1883
mqtt_object = MQTTClient() # Initialize the MQTT Class 

# Connect to MQTT broker. Returns instance of the MQTT Client that can be 
# Pass to service callses when initializing.
# @param:  client_id, a unique client ID  
mqtt_client = mqtt_object.start(MQTT_CLIENT_ID) 
```

### Light service ###
```python
# Initialize Light service 
# @param mqtt_client :an instance of a mqtt client.
# @param path : Default path where lighting animations stored. Can be overrode in the play_lb_csv_animation function
lights = LightService(mqtt_client = mqtt_client, path = os.getcwd()) 

# Play a light bar animation from CSV file
# @param  csv_file: the name of the csv_file
# @param path: Optional. Path to CSV file if it is different from the default path set in the LightService Init
# @param granularity: Optional: Defaut 0 
# @param crossfade: Optional: Default 1
lights.play_lb_csv_animation(csv_file, path, granularity, corssfade):

```

### Button Service ### 
```python 

# Initialize the button service 
# @param mqtt_client :an instance of a mqtt client.
button = ButtonService(mqtt_client = mqtt_client)

# Register button callback 
# @param callback: callback function 
buttion.subscribe(callback = button_callback)

# Button Callback example 
# Receives "short", "medium", "long"
def button_callback(press):
    logger.debug(f"Recieved Press {press}")
    # User Code Here
```

### Audio Service ### 
```python 

# Initialize the button service 
# @param mqtt_client :an instance of a mqtt client.
# @param path : Default path where lighting animations stored. Can be overrode in the play functions
audio = AudioService(mqtt_client = mqtt_client, path = os.getcwd())

# Play foreground audio from a file
# @param file: the name of the file to be played 
# @param path: Optional. Override the default path set when initializing the class
audio.play_foreground(file = "2SPLfltup-horn.wav", path = None)

# Play foreground audio from a file
# @param file: the name of the file to be played 
# @param path: Optional. Override the default path set when initializing the class
audio.play_background(file = "2SPLfltup-horn.wav", path = None)

# Stop all audio
audio.stop()
```

### NFC Service ### 
```python 

# Initialize the NFC service 
# @param mqtt_client :an instance of a mqtt client.
nfc = NFCService(mqtt_client = mqtt_client)

# Register NFC message callback 
# @param callback: callback function 
nfc.subscribe(callback = nfc_callback)

# Button Callback example 
# @parameter records: a list of records from the NFC services.
def nfc_callback(records):
    logger.debug(f"Recieved Press {records}")
    # User Code Here
```

### IMU Service ### 
```python 
# Initialize the IMU service 
# @param mqtt_client :an instance of a mqtt client.
imu = IMUService(mqtt_client)

# Register orientation change callback 
# @param callback: callback function 
imu.subscribe_orientation(orientation_cb)

def orientation_callback(orientation):
    logger.debug(f"IMU orientation {orientation}")

# Register for wakeup event callback 
# @param callback: callback function 
imu.subscribe_on_wake(on_wake_cb)

def imu_on_wake_callback(wake_status:'bool'):

    if wake_status == True: 
        logger.debug(f"Wand is active {wake_status}")
    elif wake_status == False: 
        logger.debug(f"Wand is inactive {wake_status}")
    else:    
        logger.debug(f"Unknown active state {wake_status}")


# Register for raw IMU data stream. NOTE this will start a data stream of IMU data
# It is up to the user to turn this stream off before the program is terminated 
# @param callback: callback function 
imu.subscribe_stream(imu_stream_cb)

# Disable Stream.
# Put in sig handler to catch termination signals
imu.disable_stream()

# Stream call back example
def imu_stream_callback(stream):
    logger.debug(f"IMU stream {stream}")


```
