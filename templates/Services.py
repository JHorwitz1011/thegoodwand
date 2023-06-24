from paho.mqtt import client as mqtt_client
import sys, os, inspect
import json

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from log import log



DEFAULT_BROKER = 'localhost'
DEFAULT_PORT = 1883


DEBUG_LEVEL = "WARNING"
LOGGER_NAME = __name__
logger = log(name = LOGGER_NAME, level = DEBUG_LEVEL)

class ChargerService():

    SERVICE_TYPE = "UI_CHARGER"
    SERVICE_VERSION = "1"
    
    STATUS_TOPIC = "goodwand/battery/status"
    FAULT_TOPIC = "goodwand/battery/faults"

    def __init__(self, mqtt_client) -> None:
        self.client = mqtt_client
        self.fault_callback = None
        self.status_callback = None


    def on_fault(self, callback, qos=0):
        
        self.client.message_callback_add(self.FAULT_TOPIC, self.__on_fault_message)
        self.client.subscribe(self.FAULT_TOPIC, qos)
        self.fault_callback = callback   
    
    def on_status(self, callback, qos=0):
        
        self.client.message_callback_add(self.STATUS_TOPIC, self.__on_status_message)
        self.client.subscribe(self.STATUS_TOPIC, qos)
        self.status_callback = callback   

    def unsubscribe(self):
        """Unsubscribe from button service callbacks"""
        pass

    def is_active(self)->'bool':
        """TODO send command to IMU to query if the wand is active"""
        pass

    ### Private Methods ### 

    def __on_status_message(self, client, userdata, message): 
        
        logger.debug(f"On status {message.payload}") 
        msg = json.loads(message.payload)

        if self.status_callback: 
            self.status_callback(msg["data"]["status"])
        else: 
            logger.warning(f"status callback not set")        

    def __on_fault_message(self,client, userdata, message):
        """Parse data and call subscriber callback"""
        logger.debug(f"On fault {message.payload}")
        msg = json.loads(message.payload)

        if self.fault_callback:       
            self.fault_callback(msg["data"]["faults"])
        else: 
            logger.warning(f"Fault callback not set")
     
    def __on_subscribe(self, client, userdata, mid, granted_qos):
        pass 

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
        return True

    def disable_stream(self):
        self.__set_stream(False)  
        return False 

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
            self.on_wake_callback(msg["status"])
        else: 
            logger.warning(f"IMU Orientation callback not set")        

    def __on_orientation(self,client, userdata, message):
        """Parse data and call subscriber callback"""
        logger.debug(f"IMU Guesture {message.payload}")
        msg = json.loads(message.payload)

        if self.orientation_callback:       
            self.orientation_callback(msg["data"]["orientation"])
        else: 
            logger.warning(f"IMU Orientation callback not set")
     
    def __on_stream(self,client, userdata, message):
        """Parse data and call subscriber callback"""
        logger.debug(f"IMU Stream {message.payload}")
        msg = json.loads(message.payload)

        if self.stream_callback:
             self.stream_callback(msg)

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
        
        msg = json.loads(message.payload)
        logger.debug(f"NFC {msg}")
        if self.callback:
            self.callback(msg)
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

    def stop(self):
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
            self.callback(msg["data"]["event"])
        else: 
            logger.warning(f"Button callback not set")
 
    def __on_subscribe(self, client, userdata, mid, granted_qos):
        pass 

# TODO System animations and Button Animations
# TODO hsv control
class LightService():

    LIGHT_BAR_TOPIC = "goodwand/ui/view/lightbar"
    MAIN_LED_TOPIC = "goodwand/ui/view/main_led"

    SERVICE_TYPE = "UI_LIGHTBAR"
    SERVICE_VERSION ="1"

    #mask vars for color manipulation
    MASK_C1 = 0x00FF0000
    MASK_C2 = 0x0000FF00
    MASK_C3 = 0x000000FF

    SHIFT_C1 = 16
    SHIFT_C2 = 8
    SHIFT_C3 = 0

    #HB defaults
    DEFAULT_MIN_BRIGHTNESS  = 0
    DEFAULT_MAX_BRIGHTNESS  = 255
    DEFAULT_RAMP_TIME       = 500000
    DEFAULT_DELAY           = 500000

    def __init__(self, mqtt_client, path = None) -> None:
        self.client = mqtt_client
        self.callback = None
        
        # Default path for light animations. Can be overrode in the animation methods
        self.path = path     

    def subscribe(self, callback, qos=0):
        pass

    def unsubscribe(self):
        """Unsubscribe from button service callbacks"""
        pass
    
    ### LIGHTBAR
    def lb_csv_animation(self, csv_file, path = None, granularity = 1, corssfade = 0):
        
        if (path == None) and (self.path == None):
            logger.warning("path to animation is undefined")
            return
        
        elif (path == None) and (self.path):
            logger.debug(f"Using defult path {self.path}")
            path = self.path
        
        header = {"type": self.SERVICE_TYPE, "version": self.SERVICE_VERSION}
        data = {"format": "animation", "animation" : csv_file}

        self.__publish_message_lightbar({"header": header, "data": data})
    

    def lb_system_animation(self, animation):  
        "make sure to exclude .csv from system animation name"      
        header = {"type": self.SERVICE_TYPE, "version": self.SERVICE_VERSION}
        data = {"animation" : animation}

        self.__publish_message_lightbar({"header": header, "data": data})
    
    def lb_block(self, r, g, b): 
        header = {"type": self.SERVICE_TYPE, "version": self.SERVICE_VERSION}
        data = {"format" : "block", "color": self.__color_cast(r,g,b)}
        self.__publish_message_lightbar({"header": header, "data": data})

    def lb_raw(self, raw: list(tuple(int,int,int)) ):
        header = {"type": self.SERVICE_TYPE, "version": self.SERVICE_VERSION}
        data = {"format" : "raw", "raw": raw}
        self.__publish_message_lightbar({"header": header, "data": data})

    def lb_heartbeat(self, r,g,b, min_brightness=DEFAULT_MIN_BRIGHTNESS, max_brightness=DEFAULT_MAX_BRIGHTNESS, ramp_time=DEFAULT_RAMP_TIME, delay_time=DEFAULT_DELAY):
        header = {"type": self.SERVICE_TYPE, "version": self.SERVICE_VERSION}
        data = {"format" : "heartbeat", "min_brightness": min_brightness, "max_brightness":max_brightness, "color": self.__color_cast(r,g,b), "delay_time":delay_time, "ramp_time":ramp_time}
        self.__publish_message_lightbar({"header": header, "data": data})

    def lb_clear(self):
        header = {"type": self.SERVICE_TYPE, "version": self.SERVICE_VERSION}
        data = {"format" : "none"}
        self.__publish_message_lightbar({"header": header, "data": data})

    ### BUTTON
    def bl_block(self, r, g, b): 
        header = {"type": self.SERVICE_TYPE, "version": self.SERVICE_VERSION}
        data = {"format" : "block", "color": self.__color_cast(r,g,b)}
        self.__publish_message_buttonled({"header": header, "data": data})

    def bl_raw(self, raw: list(tuple(int,int,int)) ):
        header = {"type": self.SERVICE_TYPE, "version": self.SERVICE_VERSION}
        data = {"format" : "raw", "raw": raw}
        self.__publish_message_buttonled({"header": header, "data": data})

    def bl_heartbeat(self, r,g,b, min_brightness=DEFAULT_MIN_BRIGHTNESS, max_brightness=DEFAULT_MAX_BRIGHTNESS, ramp_time=DEFAULT_RAMP_TIME, delay_time=DEFAULT_DELAY):
        header = {"type": self.SERVICE_TYPE, "version": self.SERVICE_VERSION}
        data = {"format" : "heartbeat", "min_brightness": min_brightness, "max_brightness":max_brightness, "color": self.__color_cast(r,g,b), "delay_time":delay_time, "ramp_time":ramp_time}
        self.__publish_message_buttonled({"header": header, "data": data})

    def bl_clear(self):
        header = {"type": self.SERVICE_TYPE, "version": self.SERVICE_VERSION}
        data = {"format" : "none"}
        self.__publish_message_buttonled({"header": header, "data": data})

    ### Private Methods ### 
    def __color_cast(c1,c2,c3) -> int:
        return ((int(c1))&self.MASK_C1)<<self.MASK_C1 | ((int(c2))&self.MASK_C2)<<self.MASK_C2 | ((int(c3))&self.MASK_C3)<<self.MASK_C3

    def __publish_message_lightbar(self, msg):
        self.client.publish(self.LIGHT_BAR_TOPIC, json.dumps(msg))

    def __publish_message_buttonled(self, msg):
        self.client.publish(self.MAIN_LED_TOPIC, json.dumps(msg))

class UVService():

    UV_TOPIC = "goodwand/ui/view/uv"

    SERVICE_TYPE = "UI_UV"
    SERVICE_VERSION ="1"

    def __init__(self, mqtt_client) -> None:
        self.client = mqtt_client
            
    def on(self, on_time : int):
              
        header = {"type": self.SERVICE_TYPE, "version": self.SERVICE_VERSION}
        data = {"timeOn":on_time}

        self.__publish_message({"header": header, "data": data})

    # TODO, UV service needs an off function
    def off(self):
        pass 
    ### Private Methods ### 

    def __publish_message(self, msg):

        self.client.publish(self.UV_TOPIC, json.dumps(msg))

class KeywordService():
    KEYWORD_TOPIC = "goodwand/ui/controller/keyword"
    KEYWORD_CMD_TOPIC = "goodwand/ui/controller/keyword/command"

    SERVICE_TYPE = "UI_KEYWORD"
    SERVICE_VERSION ="1"

    def __init__(self, mqtt_client) -> None:
        self.client = mqtt_client
        self.callback = None

    def enable(self):
        header = {"type": self.SERVICE_TYPE, "version": self.SERVICE_VERSION}
        data = {"state":1}
        self.__publish_message({"header": header, "data": data})

    # TODO, UV service needs an off function
    def disable(self):
        header = {"type": self.SERVICE_TYPE, "version": self.SERVICE_VERSION}
        data = {"state":0}
        self.__publish_message({"header": header, "data": data})

    def subscribe(self, callback, qos=0):
        self.callback = callback
        self.client.message_callback_add(self.KEYWORD_TOPIC, self.__on_message)
        self.client.subscribe(self.KEYWORD_TOPIC, qos)

    def unsubscribe(self):
        """Unsubscribe from button service callbacks"""
        pass

    ### Private Methods ### 
    def __publish_message(self, msg):
        self.client.publish(self.UV_TOPIC, json.dumps(msg))

    def __on_message(self,client, userdata, message):
        """Parse data and call subscriber callback"""
        
        msg = json.loads(message.payload)
        keyword = msg["data"]["keyword"]

        if self.callback:
            self.callback(keyword)
        else: 
            logger.warning(f"Button callback not set")

class ButtonService():

    BUTTON_TOPIC = "goodwand/ui/controller/button"
    # Single click IDS
    SHORT_ID = 'short'
    MEDIUM_ID = 'medium'
    LONG_ID = 'long'

    # Multi click IDS
    SHORT_MULTI_ID = 'short_multi'
    SHORT_MEDIUM_ID = 'short_medium'


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
        press_id = msg["data"]["event"]
        count = int(msg["data"]["count"])              

        if self.callback:
            num_args = len(inspect.signature(self.callback).parameters) #backwards compadibility
            if num_args == 1:
                self.callback(press_id)
            elif num_args == 2:
                self.callback(press_id, count)
            else: 
                logger.warning(f"callback incorrect number of args {num_args}")    
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

    def start(self, client_id):
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