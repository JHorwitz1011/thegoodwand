#! /usr/bin/env python3
import time
import json
from paho.mqtt import client as mqtt_client
import sys

broker = 'localhost'
port = 1883
topic = "goodwand/ui/view/lightbar"
# topic = "goodwand/ui/view/main_led"
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
        # pkt = {
        #     "header": {
        #         "type": "UI_LIGHTBAR",
        #         "version": 1,
        #     },
        #     "data": {
		#         "format": "heartbeat",
        # 		"r": 0,
        #         "g": 255,
        #         "b": 255
        #     }
        # }

        # pkt = {
        #     "header": {
        #         "type": "UI_LIGHTBAR",
        #         "version": 1,
        #     },
        #     "data": {
        #         "color_space": "hsv",
		#         "format": "fire",
        # 		"color": 0x550000,
        #     }
        # }

        pkt = {
            "header": {
                "type": "UI_LIGHTBAR",
                "version": 1,
            },
            "data": {
		        "format": "animation",
        		"animation": "/home/tgw/thegoodwand/services/lights/assets/no_failed.csv"
            }
        }

        # pkt = {
        #     "header": {
        #         "type": "UI_LIGHTBAR",
        #         "version": 1,
        #     },
        #     "data": {
        #         "color_space" : "hsv",
		#         "format": "raw",
        # 		"raw": 20*[0x4400FF]
        #     }
        # }
        
        # pkt = {
        #     "header": {
        #         "type": "UI_LIGHTBAR",
        #         "version": 1,
        #     },
        #     "data": {
		#         "format": "none",
        #     }
        # }


        # pkt = {
        #     "header": {
        #         "type": "UI_MAINLED",
        #         "version": 1,
        #     },
        #     "data": {
		#         "format": "none",
        #     }
        # }

        # pkt = {
        #     "header": {
        #         "type": "UI_MAINLED",
        #         "version": 1,
        #     },
        #     "data": {
        #         "color_space": "hsv",
		#         "format": "fire",
        #         "min_brightness": 100,
        #         "delay_time": 100000,
        #         "ramp_time": 100000,
        # 		"color": 0x000000
        #     }
        # }

        # pkt = {
        #     "header": {
        #         "type": "UI_MAINLED",
        #         "version": 1,
        #     },
        #     "data": {
		#         "format": "heartbeat",
        # 		"r": 255,
        #         "g": 255,
        #         "b": 0
        #     }
        # }
        # a = 20*[0x000000
        # while True:
        #     for x in range(0, 0xFF0000, 0x020000):
        #         # a.pop(0)
        #         # a.append(x+0x00FFFF)
        #         pkt["data"]["color"] = x+0x00FFFF
        #         print(f'{pkt["data"]["color"]:#x}')
        #         client.publish(topic, json.dumps(pkt))
        #         time.sleep(.1)

        client.publish(topic, json.dumps(pkt))
        time.sleep(1)
        # result: [0, 1]
        # status = result[0]
        # if status == 0:
        #     print(f"Send {pkt} to topic `{topic}`")
        # else:
        #     print(f"Failed to send message to topic {topic}")
        # msg_count += 1
    except IndexError:
        print("ERROR: no argument given. please use format: python3 pub_client.py [animation code]")
    


def run():
    client = connect_mqtt()
    client.loop_start()


    publish(client)




if __name__ == '__main__':
    run()
