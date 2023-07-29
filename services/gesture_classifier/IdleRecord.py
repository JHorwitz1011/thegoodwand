# First, install the dependencies via:
#    $ pip3 install requests

import json
import time, hmac, hashlib
import requests
import re, uuid
import math
import signal

import sys
import os
sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
#from MQTTObject import MQTTObject
from Services import *
from log import log

# Your API & HMAC keys can be found here (go to your project > Dashboard > Keys to find this)
HMAC_KEY = "d1d9eb0237b00728aff47e11f7f5b16e"
API_KEY = "ei_6278693fa35e2537d9dc9671cdd47eefa87806ec841f9774"

# empty signature (all zeros). HS256 gives 32 byte signature, and we encode in hex, so we need 64 characters here
emptySignature = ''.join(['0'] * 64)

# use MAC address of network interface as deviceId
device_name =":".join(re.findall('..', '%012x' % uuid.getnode()))

# here we'll collect 2 seconds of data at a frequency defined by interval_ms
freq = 26 #hz

values = []
full = False

def onIMUStream(msg):
    # buffer logic; values will always be of length 200 and once it is 
    accel = msg["data"]["accel"]
    gyro = msg["data"]["gyro"]
    values.append((accel['x'], accel['y'], accel['z'], gyro['x'], gyro['y'], gyro['z']))

def onButton(msg):
    data = {
        "protected": {
            "ver": "v1",
            "alg": "HS256",
            "iat": time.time() # epoch time, seconds since 1970
        },
        "signature": emptySignature,
        "payload": {
            "device_name":  device_name,
            "device_type": "LINUX_TEST",
            "interval_ms": 1000/freq,
            "sensors": [
                { "name": "accX", "units": "m/s2" },
                { "name": "accY", "units": "m/s2" },
                { "name": "accZ", "units": "m/s2" },
                { "name": "gyroX", "units": "rad/s2" },
                { "name": "gyroY", "units": "rad/s2" },
                { "name": "gyroZ", "units": "rad/s2" }
            ],
            "values": values
        }
    }

    # encode in JSON
    encoded = json.dumps(data)

    # sign message
    signature = hmac.new(bytes(HMAC_KEY, 'utf-8'), msg = encoded.encode('utf-8'), digestmod = hashlib.sha256).hexdigest()

    # set the signature again in the message, and encode again
    data['signature'] = signature
    encoded = json.dumps(data)

    # and upload the file
    res = requests.post(url='https://ingestion.edgeimpulse.com/api/training/data',
                        data=encoded,
                        headers={
                            'Content-Type': 'application/json',
                            'x-file-name': 'unknown',
                            'x-api-key': API_KEY
                        })
    if (res.status_code == 200):
        print('Uploaded file to Edge Impulse', res.status_code, res.content)
    else:
        print('Failed to upload file to Edge Impulse', res.status_code, res.content)


mqtt_obj = MQTTClient()
mqtt_client = mqtt_obj.start("imu record")
imu = IMUService(mqtt_client)
imu.subscribe_stream(onIMUStream)
button = ButtonService(mqtt_client)
button.subscribe(onButton)

signal.pause()
