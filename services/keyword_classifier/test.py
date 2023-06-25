import sys
import os
sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from Services import *

mqtt_obj = MQTTClient()
mqtt_client = mqtt_obj.start("CONDUCTOR_CLIENT_ID")
keyword = KeywordService(mqtt_client)

def callback(keyword):
    print(f"callback, recognized {keyword}")

keyword.subscribe(callback)

print("enabling service... say some keywords! (enter to continue)")
keyword.enable()
input()


print("disabling service... try and say some keywords again nothing should show (enter to continue)")
keyword.disable()
input()