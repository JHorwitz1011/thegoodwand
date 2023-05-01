from paho.mqtt import client as mqtt_client
import json

DEFAULT_BROKER = 'localhost'
DEFAULT_PORT = 1883

class MQTTObject():
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
        self.topics_and_callbacks = {}
        self.client = None

    def start_mqtt(self, client_id, topics_and_callbacks={}):
        """
        Parameters:
            client_id (str): name to identify as 
            topics_and_callbacks (dict): dictionary with str keys describing topics to subscribe to, and values of callback functions
        """
        self.client_id = client_id
        self.topics_and_callbacks = topics_and_callbacks
        
        # Connect to client
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f"Connected {self.client_id} to MQTT Broker!")
            else:
                raise Exception(f"Failed to connect to MQTT server, return code {rc}")

        self.client = mqtt_client.Client(self.client_id)
        self.client.on_connect = on_connect
        self.client.connect(self.broker, self.port)    
        
        # Start MQTT
        # Add all callbacks
        print(self.topics_and_callbacks)
        for topic in self.topics_and_callbacks.keys():
            self.client.message_callback_add(topic, self.topics_and_callbacks[topic])
            print('subscribed to ', topic)
            self.client.subscribe(topic)
            self.client.enable_logger()
    
        self.client.loop_start()


    def connect_mqtt(self):
        """
        Connect this service to MQTT broker
        
        """
        

    def publish(self, topic: str, payload: str, qos: int = 0):
        """Publish packet to topic"""
        self.client.publish(topic, payload, qos)