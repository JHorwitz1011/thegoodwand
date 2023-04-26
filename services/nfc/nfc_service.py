#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from paho.mqtt import client as mqtt
import json
import signal 
import sys
import time
import ndef

SERVICE_TYPE = "UI_NFC"
SERVICE_VERSION = "1"

MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'goodwand/ui/controller/nfc'
MQTT_CLIENT_ID = 'TGW_NFC_SERVICE'


def mqtt_on_connect(client, userdata, flags, rc):
    if rc == 0:
        reader.READER.logger.info("Connected to MQTT Broker!")
    else:
        reader.READER.logger.warning("Failed to connect to MQTT server, return code %d\n", rc)


def mqtt_connect():
    client = mqtt.Client(MQTT_CLIENT_ID)
    client.on_connect = mqtt_on_connect
    client.connect(MQTT_BROKER, MQTT_PORT)
    return client


def mqtt_on_message(self, client, userdata, msg):
    #payload = json.loads(msg.payload)
    try:
        reader.READER.logger.info(msg)
    except KeyError:
        reader.READER.logger.warning("Json Key error")


def mqtt_on_publish(client, userdata, mid):
    pass


def mqtt_publish(client,type, version, uid, records):
    header = {"type": type, "version": version}
    card_data =   {"uid": uid, "records": records}
    msg = {"header": header, "card_data": card_data}
    reader.READER.logger.info(f"[MQTT MESSAGE]  {msg}")
    client.publish(MQTT_TOPIC, json.dumps(msg))


def mqtt_start():
    client.on_message = mqtt_on_message
    client.on_publish = mqtt_on_publish
    client.enable_logger()
    client.loop_start()
    client.disconnect

def cleanup(): 
    GPIO.cleanup()
    sys.exit(0)

class Ndef():

#NDEF byte 0
    NDEF_EMPTY_RECORD = 0X00
    NDEF_TERMINATOR = 0XFE
    NDEF_NDEF_MESSAGE = 0x03
    NDEF_PROPRIETART = 0xFD

    TEXT__RECORD_TYPE = "urn:nfc:wkt:T"
    URI_RECORD_TYPE   = "urn:nfc:wkt:U"

    def __init__(self):
        pass

    #returns the nfc card type 
    #0x03 = NDEF message
    #0xFD 
    def isNdef(self, byte_array):
        if byte_array[0] == self.NDEF_NDEF_MESSAGE:
            return True
        else:
            return False
     
    #find the termination char 0xfe.
    # return pos if successful
    # return -1 if failed
    def __getTermination(self, byte_array):
        res = -1
        for i in range(len(byte_array)):
               if byte_array[i] == self.NDEF_TERMINATOR:
                      res =  i
                      break
        return res


    def decode(self, byte_array):
        
        mqtt_data = []
        i = self.__getTermination(byte_array)
        
        if i == -1:
            reader.READER.logger.warning("Failed to find termination character")
            return []
        
        for record in ndef.message_decoder(byte_array[2:i]): 
            reader.READER.logger.debug(f"{record}  {type(record)}")
            
            if record.type == "urn:nfc:wkt:T":
                reader.READER.logger.debug(f"[TEXT RECORD] {record.type}")
                mqtt_data.append({"type": "text", "data" : record.text})
            
            elif record.type == "urn:nfc:wkt:U":
                reader.READER.logger.debug(f"[URI RECORD]  {record.type}")  
                mqtt_data.append({"type": "uri", "data" : record.iri}) 
            
            #Custom Type. 
            else: 
                reader.READER.logger.debug(f"[Unknown Record Type] {record.type}  {record.data}")
                mqtt_data.append({"type": record.type, "data" : record.data.decode("utf-8")}) 
                

        
        return mqtt_data


if __name__ == '__main__': 

    reader = SimpleMFRC522()
    ndef_helper = Ndef()

    client = mqtt_connect()
    mqtt_start()

    while 1: 
        try:
            id, text = reader.read(.25) #added delay to prevent 100% CPU usage
            message_byte_array = text.encode('latin-1')
            
            reader.READER.logger.debug(f'[RAW DATA  [UID]{id} \t [DATA]{text}')
            
            if len(message_byte_array):
                #Is the data NDEF encoded
                if ndef_helper.isNdef(message_byte_array):
                    mqtt_data = (ndef_helper.decode(message_byte_array)) 

                else:
                    mqtt_data.append(text) 
                
                mqtt_publish(client, SERVICE_TYPE, SERVICE_VERSION, id, mqtt_data)
                time.sleep(.25) 

            else:
                reader.READER.logger.warning("Error reading card data  {message_byte_array}")
        except KeyboardInterrupt:
            cleanup()
        except:
            cleanup()
    