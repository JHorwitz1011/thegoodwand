import sys
import os
sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from Services import *
import time

mqtt_obj = MQTTClient()
mqtt_client = mqtt_obj.start("CONDUCTOR_CLIENT_ID")
keyword = KeywordService(mqtt_client)

def callback(keyword):
    print(f"callback, recognized {keyword}")

keyword.subscribe(callback)
while(1):
    print("enabling service... say some keywords! (enter to continue)")
    keyword.enable()
    # time.sleep(sys.argv[1])
    input()


    print("disabling service... try and say some keywords again nothing should show (enter to continue)")
    keyword.disable()
    # time.sleep(sys.argv[1])
    input()

