echo "Creating the Supervisor configuration files"

#Pass $USER as the first argument to auto set the path
#
if [ $1 ]
then 
    path=$1
else
    echo "Error: Missing Path argument"; exit 1
fi

if [ $2 ]
then 
user=$2

 else 
    echo "Missing user argument"; exit 1
fi

echo "Creating Lightbar service"
#supervisor config files: ONLY SERVICE THAT NEEDS ROOT user
echo "[program:lightbar]
command=python3 -u FWLightService.py
directory=home/"$path"/lights
autostart=true
autorestart=true
priority=25
user=root
"  > /etc/supervisor/conf.d/lightbar.conf
if [ $? != 0 ]
then 
    echo "ERROR: Adding Light service";
fi

echo "Creating Button Service"
echo "[program:button]
command=python3 -u button_service.py
directory=home/"$path"/button
autostart=true
autorestart=true
priority=50
user=$user
"  > /etc/supervisor/conf.d/button.conf
if [ $? != 0 ]
then 
    echo "ERROR: Adding Button service";
fi


echo "Creating Audio Service"
echo "[program:audio]
command=python3 -u FWAudioService.py
directory=home/"$path"/audio
autostart=true
autorestart=true
priority=50
user=$user
" > /etc/supervisor/conf.d/audio.conf
if [ $? != 0 ]
then 
    echo "ERROR: Adding Audio service";
fi


echo "Creating NFC Service"
echo "[program:nfc]
command=python3 -u nfc_service.py
directory=home/"$path"/nfc
autostart=true
autorestart=true
priority=50
user=$user
" > /etc/supervisor/conf.d/nfc.conf
if [ $? != 0 ]
then 
    echo "ERROR: Adding NFC service";
fi


echo "Creating UV Service"
echo "[program:uv]
command=python3 -u uv_service.py
directory=home/"$path"/uvlight
autostart=true
autorestart=true
priority=50
user=$user
" > /etc/supervisor/conf.d/uv.conf
if [ $? != 0 ]
then 
    echo "ERROR: Adding UV service";
fi


echo "Creating IMU Service"
echo "[program:accel]
command=python3 -u imu_service.py
directory=home/"$path"/imu
autostart=true
autorestart=true
priority=50
user=$user
" > /etc/supervisor/conf.d/accel.conf
if [ $? != 0 ]
then 
    echo "ERROR: Adding ACCEL service";
fi

echo "Creating Backend Service"
echo "[program:backend]
command=python3 -u TGWBackend.py
directory=home/"$path"/backend
autostart=true
autorestart=true
priority=50
user=$user
" > /etc/supervisor/conf.d/backend.conf
if [ $? != 0 ]
then 
    echo "ERROR: Adding BACKEND service";
fi



echo "Creating Conductor Service"
echo "[program:conductor] 
command=python3 -u TGWConductor.py 
directory=home/"$path"/conductor 
autostart=true 
autorestart=true
priority=999
user=$user
" > /etc/supervisor/conf.d/conductor.conf
if [ $? != 0 ]
then 
    echo "ERROR: Adding Conductor service";
fi

sudo supervisorctl update
sudo supervisorctl restart all