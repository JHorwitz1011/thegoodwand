
import requests
import json
import socket
import os
import subprocess
import logging
import signal
import sys
import time


DEBUG_LEVEL = "DEBUG" #
LOGGER_HANDLER=sys.stdout
LOGGER_NAME = __name__
LOGGER_FORMAT = '%(asctime)s.%(msecs)03d [%(filename)s:%(lineno)d] %(levelname)s:  %(message)s'
LOGGER_TIME_FMT = "%M:%S"
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.getLevelName(DEBUG_LEVEL))

handler = logging.StreamHandler(LOGGER_HANDLER)
handler.setLevel(logging.getLevelName(DEBUG_LEVEL))
format = logging.Formatter(LOGGER_FORMAT,datefmt = LOGGER_TIME_FMT )
handler.setFormatter(format)
logger.addHandler(handler)



class backEnd():

    def getWandID (self) -> str:
        hostname = socket.gethostname()
        URL = 'https://www.thegoodwand.com/_functions/wandid'
        PARAMS = 'name='+hostname
        logger.debug (f"Sending GET url= {URL} for {PARAMS}")
        response = requests.get(url=URL, params=PARAMS)
        logger.debug (f"The Response is" + response.text)
        logger.debug (f"The Response status code is " + str(response.status_code))
        resp_dict = response.json ()
        wandId = str(resp_dict["_id"])
        logger.info (f"{hostname} id is {wandId}")
        return wandId

    def wandBackendSignin(self, wandId):
        res = str(subprocess.check_output(['hostname', '-I'])).split(' ')[0].replace("b'", "")
        wifiNetName = str(subprocess.check_output(['iwgetid -r'], shell=True)).split('\'')[1][:-2]
        logger.debug(f"Your IP is {res} and network name is: {wifiNetName}")
        hostname = socket.gethostname()
        url = 'https://www.thegoodwand.com/_functions/tgw' 
        headers = {'Content-Type':'application/json'}
        data = '{"_id":"'+wandId+'","title":"'+hostname+'", "ipAddress":"'+res+'", "wifiNetwork":"'+wifiNetName+'" }'
        dataS = json.dumps(data)
        response = requests.request("PUT", url, data=data, headers=headers)
        logger.info(f"Updated back end. status is {response.text}")


    def run(self):
        ## Now lets post the IP Address with our UID
        wandId = self.getWandID ()
        
        while True:
            ### Now post the data every five minutes
            self.wandBackendSignin(wandId)
            time.sleep(300)
            logger.debug(f"Backend Just finished sleeping")
        signal.pause()



if __name__ == '__main__':
	service = backEnd()
	logger.info(f"Backend running")
	service.run()