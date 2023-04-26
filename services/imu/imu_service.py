import time
import sys, signal, getopt
from paho.mqtt import client as mqtt
import json
from lsm6dsox import *
import RPi.GPIO as GPIO

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
MQTT_TOPIC_DATA = MQTT_TOPIC_BASE  +'/data'
MQTT_TOPIC_COMMAND = MQTT_TOPIC_BASE + '/command'
MQTT_TOPIC = MQTT_TOPIC_BASE + '/#'  
MQTT_CLIENT_ID = 'TGW_IMU_SERVICE'

IMU_6D_LABLES = {-1: "unknown", 1: "X-", 2: "X+", 4: "Y-", 8: "Y+", 16: "Z-", 32: "Z+"}
IMU_STATUS_LABLES = { 0: "inactive", 1: "active"}


# Configuration variables
D6D_ENABLED = True
WAKE_STATUS_ENABLED = True
RAW_DATA_ENABLED = False


def is_awake(val):
    if(val & 0x10):
        print("Inactive")
        res = False
    else:
        print("Active")
        res = True
    return res

class imu_service: 

    def __init__(self, arg = None):
        
        self.imu = LSM6DSOX(acc_odr = CTRL1_XL_ODR_26_HZ,
                    gyro_odr = CTRL2_G_ODR_26_HZ,
                    acc_scale = CTRL1_XL_SCALE_4G,
                    gyro_scale = CTRL2_G_SCALE_1000DPS,
                    mag_scale= MAG_CTRL2_FS_16G,
                    mag_enable= False,
                    debug_level="WARNING")
        
        orientaion = -1
        wake_status = -1


    def mqtt_on_connect(self, client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect to MQTT server, return code %d\n", rc)


    def mqtt_connect(self):
        client = mqtt.Client(MQTT_CLIENT_ID)
        client.on_connect = self.mqtt_on_connect
        client.connect(MQTT_BROKER, MQTT_PORT)
        return client

    # Message callback for the subtopic goodwand/ui/controller/gesture/command 
    # TODO major refactor needed to clean up all the if staments and add the other service command 
    def mqtt_on_command(self, client, userdata, message):
        msg_json = json.loads(message.payload)

        try: 
            if msg_json["header"]["type"] == SERVICE_TYPE and msg_json["data"]["type"] == "command":
                if msg_json["data"]["command"] == 'data':
                    val = msg_json["data"]["rate"]
                    if val == 1: 
                        self.imu.enable_data_ready_int(service.data_ready_callback,accel=True, gyro=True)
                    else:
                        self.imu.disable_data_ready_int()

            else: 
                print("Unknown commnad\n" + msg_json)
        except:
            print("Command error " + json.loads(message.payload))

    def mqtt_on_publish(self, client, userdata, mid):
        pass

    
    def mqtt_on_subscribe(self, client, userdata, mid, qos):
        print("subscribed")
        pass


    def mqtt_publish_guesture(self, client,type, version, gesture, xyz, imu_status):
        header = {"type":type, "version":version}
        data =   {"gesture":gesture, "orientation": xyz, "active": imu_status}
        msg = {"header": header, "data": data}
        client.publish(MQTT_TOPIC_BASE, json.dumps(msg))


    def mqtt_publish_raw(self, client ,type, version, accel, gyro):
        header = {"type":type, "version":version}
        accel_data = {"x": accel[0], "y": accel[1], "z": accel[2]}
        gyro_data =  {"x": gyro[0], "y": gyro[1], "z": gyro[2]}
        data = {"accel" : accel_data, "gyro" : gyro_data}   
        msg = {"header": header, "data": data}
        client.publish(MQTT_TOPIC_DATA, json.dumps(msg))


    def mqtt_start(self):
        client.on_message = self.mqtt_on_command
        
        self.mqtt_publish_guesture(client,SERVICE_TYPE, SERVICE_VERSION, imu_gesture, \
                    self.orientaion, self.wake_status)
        
        client.subscribe(MQTT_TOPIC_COMMAND)
        client.enable_logger()
        client.loop_start()
        client.disconnect

    def imu_on_d6d_change(self, val):
        print(f"Position Change {IMU_6D_LABLES[val&0x3F]}")
        self.orientaion = val&0x3F
        self.mqtt_publish_guesture(client,SERVICE_TYPE, SERVICE_VERSION, imu_gesture, \
                    self.orientaion, self.wake_status)
        
    def imu_on_wakeup(self, val):  
        self.wake_status = is_awake(val)
        self.mqtt_publish_guesture(client,SERVICE_TYPE, SERVICE_VERSION, imu_gesture, \
                    self.orientaion, self.wake_status)

    # Call back for accelerometer and gyrometer new data sample ready 
    # Publishes xyz data to the raw topic 
    # Works up to 26Hz sampling
    def data_ready_callback(self):
        service.mqtt_publish_raw(client, SERVICE_TYPE, SERVICE_VERSION, service.imu.getAccData(), service.imu.getGyroData() )
    
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
    client = service.mqtt_connect()
    service.mqtt_start()

    #Enable interrupt events
    if D6D_ENABLED:service.imu.enable_d6d_event(service.imu_on_d6d_change, SIXD_THS_70D) #Enable 6d orientation interrupts on INT1
    if WAKE_STATUS_ENABLED: service.imu.enable_sleep_change_event(service.imu_on_wakeup,wake_ths= 0x01, wake_dur=0x01)  #Enable wakeup interrupts on INT1
    if RAW_DATA_ENABLED: service.imu.enable_data_ready_int(service.data_ready_callback,accel=True, gyro=True) # Raw data on INT2

    # while 1:
    #     pass
    # while True: 

    #     if service.imu.get_status():
    #         accel = service.imu.getAccData()
    #         gyro  = service.imu.getGyroData()
    #         #mag   = service.imu.get_mag_data()
    #         print("[A]\tX: {0:.3f}mg    Y: {1:.3f}mg    Z: {2:.3f}mg".format(accel[0],accel[1], accel[2]))
    #         print("[G]\tX: {0:.3f}mdps  Y: {1:.3f}mdps  Z: {2:.3f}mdps".format(gyro[0],gyro[1], gyro[2]))
    #        # print("[M]\tX: {0:.3f}mGs   Y: {1:.3f}mGs   Z: {2:.3f}mGs".format(mag[0],mag[1], mag[2]))
    #         print("\n")
    #         time.sleep(1)

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()