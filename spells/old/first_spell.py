#! /usr/bin/env python3
import time
import json
from paho.mqtt import client as mqtt_client
import sys

broker = 'localhost'
port = 1883
light_topic = "goodwand/ui/view/lightbar"
audio_topic = "goodwand/ui/view/audio_playback"

# generate client ID with pub prefix randomly
client_id = f'temp-test-client'


start_audio_pkt = {
    "header": {
      "type": "UI_AUDIO", "version": 1
},
    "data": {
     "action": "START", "file": "TSShake.wav"
}
}

stop_audio_pkt = {
    "header": {
       "type": "UI_AUDIO", "version": 1
}, "data": {
  "action": "STOP"
}
}

light_pkt = {
            "header": {
                "type": "UI_LIGHTBAR",
                "version": 1,
            },
            "data": {
                        "granularity": 1,
                        "animation": f"{sys.argv[1]}",
                "crossfade": 0
            }
        }


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


def publish(client, topic, pkt):
    msg_count = 0
    time.sleep(1)
    try:
        result = client.publish(topic, json.dumps(pkt))
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send {pkt} to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1
    except IndexError:
        print("ERROR: no argument given. please use format: python3 pub_client.py [animation code]")


def run():
    client = connect_mqtt()
    client.loop_start()
    start_time = time.time()
    publish(client, audio_topic, start_audio_pkt)
    while time.time() - start_time  < 3:
       publish(client, light_topic, light_pkt)
       time.sleep(.5)
    publish(client, light_topic, stop_audio_pkt)


if __name__ == '__main__':
    run()
