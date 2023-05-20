from paho.mqtt import client as mqtt_client
import sys, os
import json

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from log import log



DEFAULT_BROKER = 'localhost'
DEFAULT_PORT = 1883


DEBUG_LEVEL = "WARNING"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)

# TODO Add is active and wake up callback
class IMUService():

    SERVICE_TYPE = "UI_GESTURE"
    SERVICE_VERSION = "1"
    
    ORIENTATION_TOPIC = "goodwand/ui/controller/gesture"
    STREAM_TOPIC = ORIENTATION_TOPIC + "/data"
    COMMAND_TOPIC = ORIENTATION_TOPIC + "/command"
    IS_ACTIVE_TOPIC = ORIENTATION_TOPIC + "is_active"  # Subscribe
    ON_WAKE_TOPIC = ORIENTATION_TOPIC + "/on_wake"     # Subscribe 

    def __init__(self, mqtt_client) -> None:
        self.client = mqtt_client
        self.orientation_callback = None
        self.stream_callback = None
        self.on_wake_callback = None


    def subscribe_stream(self, callback, qos=0):
        
        self.client.message_callback_add(self.STREAM_TOPIC, self.__on_stream)
        self.client.subscribe(self.STREAM_TOPIC, qos)
        self.stream_callback = callback

    def subscribe_orientation(self, callback, qos=0):
        
        self.client.message_callback_add(self.ORIENTATION_TOPIC, self.__on_orientation)
        self.client.subscribe(self.ORIENTATION_TOPIC, qos)
        self.orientation_callback = callback   
    
    def subscribe_on_wake(self, callback, qos=0):
        
        self.client.message_callback_add(self.ON_WAKE_TOPIC, self.__on_wake)
        self.client.subscribe(self.ON_WAKE_TOPIC, qos)
        self.on_wake_callback = callback   

    def enable_stream(self):
        self.__set_stream(True)

    def disable_stream(self):
        self.__set_stream(False)   

    def unsubscribe(self):
        """Unsubscribe from button service callbacks"""
        pass

    def is_active(self)->'bool':
        """TODO send command to IMU to query if the wand is active"""
        pass

    ### Private Methods ### 

    def __set_stream(self, enable:'bool'):
        events =   {"raw":enable, "wake": True, "orientation": True}
        msg = {"type": "event_command", "data": events}
        self.__publish_command(msg)

    def __publish_command(self, message):
        self.client.publish(self.COMMAND_TOPIC, json.dumps(message))
        pass

    def __on_wake(self, client, userdata, message): 
        
        logger.debug(f"On Wake {message.payload}") 
        msg = json.loads(message.payload)
        if self.on_wake_callback:       
            try:
                self.on_wake_callback(msg["status"])
            except Exception as e:
                logger.warning(f"Json Paring error {e}")
        else: 
            logger.warning(f"IMU Orientation callback not set")        

    def __on_orientation(self,client, userdata, message):
        """Parse data and call subscriber callback"""
        logger.debug(f"IMU Guesture {message.payload}")
        msg = json.loads(message.payload)

        if self.orientation_callback:       
            try:
                self.orientation_callback(msg["data"]["orientation"])
            except Exception as e:
                logger.warning(f"Json Paring error {e}")
        else: 
            logger.warning(f"IMU Orientation callback not set")
     
    def __on_stream(self,client, userdata, message):
        """Parse data and call subscriber callback"""
        logger.debug(f"IMU Stream {message.payload}")
        msg = json.loads(message.payload)

        if self.stream_callback:
            try:
                self.stream_callback(msg)
            except Exception as e:
                logger.warning(f"Json Paring error {e}")
        else: 
            logger.warning(f"NFC callback not set")
    def __on_subscribe(self, client, userdata, mid, granted_qos):
        pass 


# TODO Determine correct behavior for callback to support Yoto cards
# Maybe have a differnt callback for Yoto and TGW tags
class NFCService():

    NFC_TOPIC = "goodwand/ui/controller/nfc"

    def __init__(self, mqtt_client) -> None:
        self.client = mqtt_client
        self.callback = None

    def subscribe(self, callback, qos=0):
        
        self.client.message_callback_add(self.NFC_TOPIC, self.__on_message)
        self.client.subscribe(self.NFC_TOPIC, qos)
        self.callback = callback

    def unsubscribe(self):
        """Unsubscribe from button service callbacks"""
        pass


    ### Private Methods ### 

    def __on_message(self,client, userdata, message):
        """Parse data and call subscriber callback"""
        logger.debug(f"NFC {message.payload}")
        msg = json.loads(message.payload)

        if self.callback:
            pass
            try:
                self.callback(msg)
            except Exception as e:
                logger.warning(f"Json Paring error {e}")
        else: 
            logger.warning(f"NFC callback not set")
 
    def __on_subscribe(self, client, userdata, mid, granted_qos):
        pass 


class AudioService():

    AUDIO_TOPIC = "goodwand/ui/view/audio_playback"

    SERVICE_TYPE = "UI_AUDIO"
    SERVICE_VERSION ="1"
    MQTT_HEADER = {"type": SERVICE_TYPE, "version": SERVICE_VERSION}

    MODE_BACKGROUND = "background"
    MODE_FOREGROUND = "foreground"

    def __init__(self, mqtt_client, path = None) -> None:
        self.client = mqtt_client
        self.callback = None
        self.path = path 

    def subscribe(self, callback, qos=0):
        pass

    def unsubscribe(self):
        """Unsubscribe from button service callbacks"""
        pass
    
    def play_foreground(self, file, path = None):
        self.__play_file(file = file, mode = self.MODE_FOREGROUND, path = path)

    def play_background(self, file, path = None):
        self.__play_file(file = file, mode = self.MODE_BACKGROUND, path = path)
    
    def play_system(self, animation):
        pass

    def stop_audio(self):
        data = {"action":"STOP", "path": None, "file":None, "mode":None }
        self.__publish_message({"header": self.MQTT_HEADER, "data": data})
        

    ### Private Methods ### 

    def __play_file(self, file, mode, path = None):
        
        if (path == None) and (self.path == None):
            logger.warning("path to audio is undefined")
            return
        
        elif (path == None) and (self.path):
            logger.debug(f"Using defult path {self.path}")
            path = self.path
        
        data = {"action":"START", "path": path, "file":file, "mode":mode }
        self.__publish_message({"header": self.MQTT_HEADER, "data": data})

    def __publish_message(self, msg):

        self.client.publish(self.AUDIO_TOPIC, json.dumps(msg))

    def __on_message(self,client, userdata, message):
        """Parse data and call subscriber callback"""
        
        msg = json.loads(message.payload)
        if self.callback:
            try:
                self.callback(msg["data"]["event"])
            except Exception as e:
                logger.warning(f"Json Paring error {e}")
        else: 
            logger.warning(f"Button callback not set")
 
    def __on_subscribe(self, client, userdata, mid, granted_qos):
        pass 


# TODO System animations and Button Animations
class LightService():

    LIGHT_BAR_TOPIC = "goodwand/ui/view/lightbar"
    MAIN_LED_TOPIC = "goodwand/ui/view/main_led"

    SERVICE_TYPE = "UI_LIGHTBAR"
    SERVICE_VERSION ="1"

    def __init__(self, mqtt_client, path = None) -> None:
        self.client = mqtt_client
        self.callback = None
        
        # Default path for light animations. Can be overrode in the play methods
        self.path = path 

    def subscribe(self, callback, qos=0):
        pass

    def unsubscribe(self):
        """Unsubscribe from button service callbacks"""
        pass
    
    def play_lb_csv_animation(self, csv_file, path = None, granularity = 1, corssfade = 0):
        
        if (path == None) and (self.path == None):
            logger.warning("path to animation is undefined")
            return
        
        elif (path == None) and (self.path):
            logger.debug(f"Using defult path {self.path}")
            path = self.path
        
        header = {"type": self.SERVICE_TYPE, "version": self.SERVICE_VERSION}
        data = {"granularity":granularity, "animation" : csv_file, "path": path, "crossfade":corssfade }

        self.__publish_message({"header": header, "data": data})
    

    def play_lb_system_animation(self, animation):
        pass


    ### Private Methods ### 

    def __publish_message(self, msg):

        self.client.publish(self.LIGHT_BAR_TOPIC, json.dumps(msg))

    def __on_message(self,client, userdata, message):
        """Parse data and call subscriber callback"""
        
        msg = json.loads(message.payload)
        if self.callback:
            try:
                self.callback(msg["data"]["event"])
            except Exception as e:
                logger.warning(f"Json Paring error {e}")
        else: 
            logger.warning(f"Button callback not set")
 
    def __on_subscribe(self, client, userdata, mid, granted_qos):
        pass 


class ButtonService():

    BUTTON_TOPIC = "goodwand/ui/controller/button"

    def __init__(self, mqtt_client) -> None:
        self.client = mqtt_client
        self.callback = None

    def subscribe(self, callback, qos=0):
        
        self.client.message_callback_add(self.BUTTON_TOPIC, self.__on_message)
        self.client.subscribe(self.BUTTON_TOPIC, qos)
        self.callback = callback

    def unsubscribe(self):
        """Unsubscribe from button service callbacks"""
        pass


    ### Private Methods ### 

    def __on_message(self,client, userdata, message):
        """Parse data and call subscriber callback"""
        
        msg = json.loads(message.payload)
        if self.callback:
            try:
                self.callback(msg["data"]["event"])
            except Exception as e:
                logger.warning(f"Json Paring error {e}")
        else: 
            logger.warning(f"Button callback not set")
 
    def __on_subscribe(self, client, userdata, mid, granted_qos):
        pass 


class MQTTClient():
    """Abstracts away irrelevavnt aspects of mqtt functionality for ease of programming"""

    def __init__(self, broker=DEFAULT_BROKER, port=DEFAULT_PORT):
        """
        Parameters:
            broker (str): hostname of broker to connect to. defaults to localhost
            port (int): port to connect to. defaults to 1883
        """
        self.broker = broker
        self.port = port
        self.client_id = ''
        self.client = None

    def start_mqtt(self, client_id):
        """
        Parameters:
            client_id (str): name to identify as 
            topics_and_callbacks (dict): dictionary with str keys describing topics to subscribe to, and values of callback functions
        """
        self.client_id = client_id
        
        # Connect to client
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.info(f"{self.client_id} Connected to MQTT Broker!")
            else:
                raise Exception(f"Failed to connect to MQTT server, return code {rc}")

        self.client = mqtt_client.Client(self.client_id)
        self.client.on_connect = on_connect
        self.client.disconnect = self.on_disconnect
        self.client.connect(self.broker, self.port)    
        #self.client.enable_logger()
        self.client.loop_start()

        return self.client

    def publish(self, topic, message):
        self.client.publish(topic, message)

    def stop_mqtt(self):
        """
        Connect this service to MQTT broker
        
        """
    def on_disconnect(self):
        logger.warning(f"{self.client_id} Disconnected from the MQTT broker!")