# python 3.6

import json
import pigpio
from paho.mqtt import client as mqtt_client

broker = 'localhost'
port = 1883
uv_topic = "goodwand/ui/view/uv"

client_id = 'TGW-UVService'
PWM_FREQ = 60
PWM_UPPER_RANGE = 100
PIN = 27

class FWUVService():
    #set constants and the such
    def __init__(self):
        self.on = False
        self.brightness = 100
        self.pi = pigpio.pi()
        self.pi.set_mode(PIN, pigpio.OUTPUT)
        self.pi.set_PWM_frequency(PIN, PWM_FREQ)
        self.pi.set_PWM_dutycycle(PIN, self.on*self.brightness)
        self.pi.set_PWM_range(PIN, PWM_UPPER_RANGE)
     
    ############### MQTT ###############################
    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect to MQTT server, return code %d\n", rc)

        client = mqtt_client.Client(client_id)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client

    def on_uv_message(self, client, userdata, msg):
        payload = json.loads(msg.payload)
        try:
            on = payload["data"].get("state")
            if  on == 'on':
                on = True
            elif on == 'off':
                on = False
            else:
                raise ValueError()
            
            brightness = payload["data"].get("brightness")
            print(f"setting uv {on} to brightness level {brightness}")
            self.update_uv(on, brightness)

        except KeyError:
            print("ERROR parsing incoming message")

    ################## MAIN LOOP ##########################
    def run(self):
        client = self.connect_mqtt()
        client.on_message = self.on_uv_message

        client.subscribe(uv_topic)
        client.enable_logger()
        client.loop_forever()



    ################# LIGHT HANDLING ######################
    def update_uv(self, on, brightness):
        if on is not None:
            self.on = on
        if brightness is not None:
            self.brightness = brightness

        self.pi.set_PWM_dutycycle(PIN, self.on*self.brightness)


if __name__ == '__main__':
    service = FWUVService()  
    service.run()
