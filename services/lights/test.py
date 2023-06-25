import sys
import os
sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from Services import *

mqtt_obj = MQTTClient()
mqtt_client = mqtt_obj.start("CONDUCTOR_CLIENT_ID")
lights = LightService(mqtt_client)


print("heartbeat button")
lights.lb_csv_animation("idleDrums.csv", os.path.expanduser("~/thegoodwand/spells/idle"))
input()

