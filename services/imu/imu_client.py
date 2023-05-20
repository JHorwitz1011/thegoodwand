import sys, signal, os
from paho.mqtt import client as mqtt
import json
import RPi.GPIO as GPIO

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from log import log

DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)

MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC_BASE = 'goodwand/ui/controller/gesture'
MQTT_TOPIC_GUESTURE = MQTT_TOPIC_BASE
MQTT_TOPIC_DATA = MQTT_TOPIC_BASE  +'/data'        # Raw data sream on this topic 
MQTT_TOPIC_COMMAND = MQTT_TOPIC_BASE + '/command'  # Send IMU commands to this topic 
MQTT_CLIENT_ID = __name__

IMU_6D_LABLES = {-1: "unknown", 1: "X-", 2: "X+", 4: "Y-", 8: "Y+", 16: "Z-", 32: "Z+"}
IMU_STATUS_LABLES = { 0: "inactive", 1: "active"}


class imu_client: 

    def __init__(self, arg = None):
        pass
        
       
    def mqtt_on_connect(self, client, userdata, flags, rc):
            if rc == 0:
                logger.debug("Connected to MQTT Broker!")
            else:
                logger.warning(f"Failed to connect to MQTT server, return code {rc}")


    def mqtt_connect(self):
        client = mqtt.Client(MQTT_CLIENT_ID)
        client.on_connect = self.mqtt_on_connect
        client.connect(MQTT_BROKER, MQTT_PORT)
        logger.debug("connect to mqtt")
        return client

    def mqtt_on_publish(self, client, userdata, mid):
        pass

    
    def mqtt_on_subscribe(self, client, userdata, mid, qos):
        logger.debug("subscribed")
        pass

    ## USE THIS TO TURN ON AND OFF RAW DATA STREAM. PASS True OR False TO TURN ON AND OFF EVENTS
    def mqtt_publish_command(self, client, raw_en, wake_en, orientation_en):
        events =   {"raw":raw_en, "wake": wake_en, "orientation": orientation_en}
        msg = {"type": "event_command", "data": events}
        client.publish(MQTT_TOPIC_COMMAND, json.dumps(msg))

    ## Publish raw Accel + Gyro data

    ## example packet {"accel": {"x": -25.742, "y": -8.418, "z": 1014.7959999999999}, "gyro": {"x": 70, "y": 455, "z": -630}}
    def on_raw_data(self, client, userdata, message):
        logger.debug(f"raw {message.payload}")

    def on_guesture(self, client, userdata, message):
        logger.debug(f"guesture {message.payload}")


    def mqtt_start(self):
        
        mqtt_client.message_callback_add(MQTT_TOPIC_DATA, self.on_raw_data)   # Use callback_add to add a specific callback for the raw data topic. 
        mqtt_client.message_callback_add(MQTT_TOPIC_GUESTURE, self.on_guesture) 
        mqtt_client.subscribe(MQTT_TOPIC_DATA)    
        mqtt_client.subscribe(MQTT_TOPIC_GUESTURE)  
        
        mqtt_client.enable_logger()
        mqtt_client.loop_start()
        logger.debug("Starting MQTT")


    def run(self):
        self.mqtt_publish_command(mqtt_client, True, True, True)
        pass

# Cleanup 
def signal_handler(sig, frame): 
    # Set back to normal 
    imu_example.mqtt_publish_command(mqtt_client, False, True, True)
    #GPIO.cleanup()
    sys.exit(0)


##########MAIN#########
if __name__ == '__main__':  
    
    imu_gesture = 0 #TBD
    imu_example = imu_client()
    logger.debug("Hello")    
    #Start to MQTT service
    mqtt_client = imu_example.mqtt_connect()
    imu_example.mqtt_start()
    SLEEP_TIME = 2


    logger.debug("Turning on all events")
    imu_example.mqtt_publish_command(mqtt_client, True, True, True)

    # Examples of turning on and off different IMU events 
    # logger.debug("Turning on Raw data")
    # imu_example.mqtt_publish_command(mqtt_client, True, False, False)
    #time.sleep(SLEEP_TIME)

    # logger.debug("Turning on Wakeup")
    # imu_example.mqtt_publish_command(mqtt_client, False, True, False)
    # time.sleep(SLEEP_TIME)

    # logger.debug("Turning on Orientation ")
    # imu_example.mqtt_publish_command(mqtt_client, False, False, True)
    # time.sleep(SLEEP_TIME)

    # imu_example.mqtt_publish_command(mqtt_client, False, False, False)
    # time.sleep(SLEEP_TIME)

    

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()