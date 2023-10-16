[<- back to home](../README.md)

to download:
```
cd ~
git clone git@bitbucket.org:fishwandproto/button.git
```

```python
    # To use:

sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from Services import MQTTClient
from Services import ButtonService

# Get MQTT Client
mqtt_object = MQTTClient()
mqtt_client = mqtt_object.start(MQTT_CLIENT_ID)

# Initialize and register call back
button = ButtonService(mqtt_client)
button.subscribe(button_callback)

# Button callback. 
# Press = click type
def button_callback(press, count):
    
    # Supported button types 
    # Note some of these will be reserved for system actions
    # Follow development guides when using 
    if press == button.SHORT_ID:
        logger.debug("short press")
    elif press == button.MEDIUM_ID:
        logger.debug("medium press")
    elif press == button.LONG_ID:
        logger.debug("long press")
    elif press == button.SHORT_MULTI_ID:
        logger.debug(f"Multiple short presses {count}")
    elif press == button.SHORT_MEDIUM_ID:
        logger.debug(f"A short followed by a medium press {count}")
    else:
        logger.debug("Unknown ID")
```
