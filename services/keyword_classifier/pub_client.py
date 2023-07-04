#! /usr/bin/env python3
import time
import json
from paho.mqtt import client as mqtt_client
import sys

broker = 'localhost'
port = 1883

pkt = {
	"header": {
		"type": "UI_KEYWORD",
		"version": 1
    },
    "data": {
        "state": sys.argv[1]
    }
}
topic = "goodwand/ui/controller/keyword/command"

# generate client ID with pub prefix randomly
client_id = f'temp-test-client'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client):
    msg_count = 0
    try:
        client.publish(topic, json.dumps(pkt))
        time.sleep(1)
    except IndexError:
        print("ERROR: no argument given. please use format: python3 pub_client.py [animation code]")
    


def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)

if __name__ == '__main__':
    run()
