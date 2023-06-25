import sys
import os
sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from Services import *

mqtt_obj = MQTTClient()
mqtt_client = mqtt_obj.start("CONDUCTOR_CLIENT_ID")
lights = LightService(mqtt_client)


print("absolute path csv")
lights.lb_csv_animation("idleDrums.csv", os.path.expanduser("~/thegoodwand/spells/idle"))
input()

print("system animation")
lights.lb_system_animation("no_failed")
input()

print("block")
lights.lb_block(0, 0, 255)
input()
lights.lb_block(0, 255, 0)
input()
lights.lb_block(255, 0, 0)
input()
lights.lb_block(255,255,255)
input()

print("raw")
lights.lb_raw(5*[0xffffff, 0xff0000, 0x00ff00, 0x0000ff])
input()
lights.lb_raw(5*[0x123483, 0xaaaaaa, 0x192748, 0x888888])
input()
lights.lb_raw(5*[0x29a6f3, 0x6a9c3b, 0x92500a, 0x001100])
input()

print("heartbeat slow, red")
lights.lb_heartbeat(255, 0, 0, delay_time=1000000, ramp_time=1000000)
input()
print("heartbeat fast, blue")
lights.lb_heartbeat(0, 0, 255, delay_time=750000, ramp_time=250000)
input()
print("heartbeat faster, white")
lights.lb_heartbeat(255, 255, 255, delay_time=100000, ramp_time=100000)
input()

print("clear")
lights.lb_clear()
input()

print("fire slow, red")
lights.lb_fire(255, 0, 0)
input()
print("fire fast, blue")
lights.lb_fire(0, 0, 255)
input()
print("fire faster, white")
lights.lb_fire(255, 255, 255)
input()