import sys, signal, os
from paho.mqtt import client as mqtt
import json
from lsm6dsox import *
import RPi.GPIO as GPIO

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from log import log
from MQTTObject import MQTTObject

DEBUG_LEVEL = "DEBUG"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)

# # Used for timing debug
# GPIO.setmode(GPIO.BCM)
# PIN = 27
# pinState = False
# GPIO.setup(PIN,GPIO.OUT)
# #Insert where timing is needed
# global pinState
# pinState = not pinState
# GPIO.output(27, pinState)

SERVICE_TYPE = "UI_GESTURE"
SERVICE_VERSION = "1"

MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC_BASE = 'goodwand/ui/controller/gesture'
MQTT_TOPIC_GUESTURE = MQTT_TOPIC_BASE
MQTT_TOPIC_DATA = MQTT_TOPIC_BASE  +'/data'
MQTT_TOPIC_COMMAND = MQTT_TOPIC_BASE + '/command'
MQTT_TOPIC_IS_ACTIVE = MQTT_TOPIC_BASE + '/is_active'
MQTT_TOPIC_ON_WAKE = MQTT_TOPIC_BASE + '/on_wake'
MQTT_TOPIC = MQTT_TOPIC_BASE + '/#'  
MQTT_CLIENT_ID = 'TGW_IMU_SERVICE'

IMU_6D_LABLES = {-1: "unknown", 1: "X-", 2: "X+", 4: "Y-", 8: "Y+", 16: "Z-", 32: "Z+"}
IMU_STATUS_LABLES = { 0: "inactive", 1: "active"}


# Configuration variables
D6D_ENABLED = True
WAKE_STATUS_ENABLED = True
RAW_DATA_ENABLED = False

## Logger configuration
## Change level by changing DEBUG_LEVEL variable to ["DEBUG", "INFO", "WARNING", "ERROR"]
DEBUG_LEVEL = "INFO"
LOGGER_HANDLER=sys.stdout
LOGGER_NAME = __name__
LOGGER_FORMAT = '[%(filename)s:%(lineno)d] %(levelname)s:  %(message)s'

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.getLevelName(DEBUG_LEVEL))

handler = logging.StreamHandler(LOGGER_HANDLER)
handler.setLevel(logging.getLevelName(DEBUG_LEVEL))
format = logging.Formatter(LOGGER_FORMAT)
handler.setFormatter(format)
logger.addHandler(handler)


def is_awake(val):
    if(val & 0x10):
        logger.debug("Inactive")
        res = False
    else:
        logger.debug("Active")
        res = True
    return res


# class imu_mqtt:

#     def __init__(self):
#         pass


class imu_service: 

    def __init__(self, arg = None):
        
        self.imu = LSM6DSOX(acc_odr = CTRL1_XL_ODR_26_HZ,
                    gyro_odr = CTRL2_G_ODR_26_HZ,
                    acc_scale = CTRL1_XL_SCALE_4G,
                    gyro_scale = CTRL2_G_SCALE_1000DPS,
                    mag_scale= MAG_CTRL2_FS_16G,
                    mag_enable= False,
                    debug_level= DEBUG_LEVEL)
        
        self.orientaion = -1
        self.wake_status = -1


    def mqtt_on_connect(self, client, userdata, flags, rc):
            if rc == 0:
                logger.debug("Connected to MQTT Broker!")
            else:
                logger.warning(f"Failed to connect to MQTT server, return code {rc}")


    def mqtt_connect(self):
        client = mqtt.Client(MQTT_CLIENT_ID)
        client.on_connect = self.mqtt_on_connect
        client.connect(MQTT_BROKER, MQTT_PORT)
        return client

    
    def configure_imu(self, odr, accel_en, gyro_en):
        pass

    def enable_raw_data_event(self):
       logger.debug("Enable Raw Data")
       self.imu.enable_data_ready_int(self.data_ready_callback,accel=True, gyro=True) # Raw data on INT2
    
    def disable_raw_data(self):
        logger.debug("Disable Raw Data")
        self.imu.disable_data_ready_int()

    def enable_6d6_event(self):
       logger.debug("Enable 6D6")
       self.imu.enable_d6d_event(self.imu_on_d6d_change, SIXD_THS_70D)
    
    def disable_6d6_event(self):
        logger.debug("Disable 6D6")
        self.imu.disable_d6d_event()
    
    def enable_wakeup_event(self):
        logger.debug("Enable wakeup")
        self.imu.enable_sleep_change_event(self.imu_on_wakeup,wake_ths= 0x01, wake_dur=0x01)  #Enable wakeup interrupts on INT1 TODO Fix magic numbers
    
    def disable_wakeup_event(self):
        logger.debug("Disable wakeup")
        self.imu.disable_sleep_change_event()

    def set_events(self, enable_raw, enable_orientation, enable_wake):
        if enable_raw: self.enable_raw_data_event()
        else: self.disable_raw_data()
        
        if enable_orientation:self.enable_6d6_event()
        else: self.disable_6d6_event()
        
        if enable_wake: self.enable_wakeup_event()
        else: self.disable_wakeup_event()

    # Message callback for the subtopic goodwand/ui/controller/gesture/command 
    def mqtt_on_command(self, client, userdata, message):
        msg = json.loads(message.payload)
        logger.debug(f"Command {msg}")
        try: 
            if 'type' in msg and msg['type'] == 'event_command':
                logger.debug(f'command : {msg}')

                self.set_events(msg['data']['raw'], msg['data']['orientation'], msg['data']['wake'])
        
            
            elif 'type' in msg and msg['type'] == 'is_active':
                logger.debug(f"Active Command {self.wake_status}")
                self.mqtt_publish_active(mqtt_client, self.wake_status)
            
            else:
                logger.debug(f"Unknown command: {msg}")

        except Exception as e:
            logger.error(f"Mqtt Command error  {json.loads(message.payload)} \n{e}")

    def mqtt_on_publish(self, client, userdata, mid):
        pass

    
    def mqtt_on_subscribe(self, client, userdata, mid, qos):
        logger.debug("subscribed")
        pass

    ## Publish guesture events 
    def mqtt_publish_guesture(self, client,type, version, gesture, xyz):
        header = {"type":type, "version":version}
        data =   {"gesture":gesture, "orientation": xyz}
        msg = {"header": header, "data": data}
        client.publish(MQTT_TOPIC_GUESTURE, json.dumps(msg))

    ## Publish raw Accel + Gyro data
    def mqtt_publish_raw(self, client ,type, version, accel, gyro):
        #header = {"type":type, "version":version}
        accel_data = {"x": accel[0], "y": accel[1], "z": accel[2]}
        gyro_data =  {"x": gyro[0], "y": gyro[1], "z": gyro[2]}
        data = {"accel" : accel_data, "gyro" : gyro_data}   
        #msg = {"header": header, "data": data}
        client.publish(MQTT_TOPIC_DATA, json.dumps(data))
        logger.debug(f"[RAW] {accel_data} {gyro_data}")


    def mqtt_publish_on_wake(self, client, message):
        # Sends a bool not Json
        msg = {"status":message }
        client.publish(MQTT_TOPIC_ON_WAKE, json.dumps(msg))
    
    def mqtt_publish_active(self,client, message):
        client.publish(MQTT_TOPIC_IS_ACTIVE, json.dumps(message))
    

    def mqtt_start(self):
        mqtt_client.on_message = self.mqtt_on_command
        
        self.mqtt_publish_guesture(mqtt_client, SERVICE_TYPE, SERVICE_VERSION, imu_gesture, \
                    self.orientaion)
        
        mqtt_client.subscribe(MQTT_TOPIC_COMMAND)
        mqtt_client.enable_logger()
        mqtt_client.loop_start()
        mqtt_client.disconnect

    def imu_on_d6d_change(self, val):
        logger.debug(f"Position Change {IMU_6D_LABLES[val&0x3F]}")
        self.orientaion = val&0x3F
        self.mqtt_publish_guesture(mqtt_client,SERVICE_TYPE, SERVICE_VERSION, imu_gesture, \
                    self.orientaion)
        
    def imu_on_wakeup(self, val):  
        self.wake_status = is_awake(val)
        logger.debug(f"On Wake {self.wake_status}")
        self.mqtt_publish_on_wake(mqtt_client, self.wake_status)


    # Call back for accelerometer and gyrometer new data sample ready 
    # Publishes xyz data to the raw topic 
    # Works up to 26Hz sampling
    def data_ready_callback(self):
        service.mqtt_publish_raw(mqtt_client, SERVICE_TYPE, SERVICE_VERSION, service.imu.getAccData(), service.imu.getGyroData())
    
    def run(self):
        pass

def signal_handler(sig, frame): 
    del(service.imu)
    GPIO.cleanup()
    sys.exit(0)


##########MAIN#########
if __name__ == '__main__':  
    
    imu_gesture = 0 #TBD
    service = imu_service()
    
    #Get starting orientation and status
    service.orientaion = service.imu.get_d6d_source()
    service.wake_status = is_awake(service.imu.get_wakeup_source())
    
    #Start to MQTT service
    mqtt_client = service.mqtt_connect()
    service.mqtt_start()

    #Enable interrupt events
    service.set_events(RAW_DATA_ENABLED, D6D_ENABLED, WAKE_STATUS_ENABLED)

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()