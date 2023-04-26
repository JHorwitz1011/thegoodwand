
import requests
import json
import socket
import os

hostname = socket.gethostname()
URL = 'https://www.thegoodwand.com/_functions/wandid'
PARAMS = 'name='+hostname
print ("Sending  data:" + PARAMS)
print ("Sending GET url=" + URL)
response = requests.get(url=URL, params=PARAMS)
print ("The Response is" + response.text)
print ("The Response status code is " + str(response.status_code))
resp_dict = response.json ()
wandId = str(resp_dict["_id"])
print ("Resp uid is" + wandId)

## Now lets post the IP Address with our UID

import subprocess
res = str(subprocess.check_output(['hostname', '-I'])).split(' ')[0].replace("b'", "")
wifiNetName = str(subprocess.check_output(['iwgetid -r'], shell=True)).split('\'')[1][:-2]
print("Your IP is" + res + "and network name is:" + wifiNetName)

url = 'https://www.thegoodwand.com/_functions/tgw' 
print ("Sending PUT URL" + url)
headers = {'Content-Type':'application/json'}
data = '{"_id":"'+wandId+'","title":"'+hostname+'", "ipAddress":"'+res+'", "wifiNetwork":"'+wifiNetName+'" }'
dataS = json.dumps(data)
print ("The JSON is" + dataS)


while True:
    ### Now post the data 
    response = requests.request("PUT", url, data=data, headers=headers)
    print("Updated web Got Back:" + response.text)
    sleep(300)
    Print("Just finished sleeping")

