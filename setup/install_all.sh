#1bin/sh

if [ $USER = "root" ]
then 
    echo "ERROR: Do not run as SUDO"
    exit 1
fi

echo "Starting TGW Setup."
echo "Step 1: update and upgrade the system"

# sudo apt-get update
# if [ $? != 0 ]
# then 
#     echo "ERROR: Updating packages"; exit 1
# fi

# Required packages 
    # python3-pip
    # python3-smbus
    # mosquitto
    # mosquitto-clients
    # supervisor
    # ndeflib
    # paho-mqtt
    # sysstat

# echo "Step 2: Install required pachages"

# sudo apt-get install python3-pip
# if [ $? != 0 ]
# then 
#     echo "ERROR: Installing PIP"; exit 1
# fi

# sudo apt-get install python3-smbus
# if [ $? != 0 ]
# then 
#     echo "ERROR: Installing SMBUS"; exit 1
# fi

# sudo apt-get install -y mosquitto
# if [ $? != 0 ]
# then 
#     echo "ERROR: Installing Mosquitto"; exit 1
# fi

# sudo apt-get install -y mosquitto-clients
# if [ $? != 0 ]
# then 
#     echo "ERROR: Installing Mosquitto Client"; exit 1
# fi

# echo "Step 3: Install Supervisor"
# sudo apt-get install -y supervisor
# echo "SUPERVISOR $?"
# if [ $? != 0 ]
# then 
#     echo "ERROR: Installing Supervisor"; exit 1
# fi

# sudo pip3 install ndeflib
# if [ $? != 0 ]
# then 
#     echo "ERROR: Installing NDEFLIB"; exit 1
# fi

# sudo pip3 install paho-mqtt
# if [ $? != 0 ]
# then 
#     echo "ERROR: Installing paho-mqtt"; exit 1
# fi

# sudo apt-get install -y sysstat
# if [ $? != 0 ]
# then 
#     echo "ERROR: Installing sysstat"; exit 1
# fi

# sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
# if [ $? != 0 ]
# then 
#     echo "ERROR: Installing adafruit-circuitpython-neopixel"; exit 1
# fi

# sudo python3 -m pip install --force-reinstall adafruit-blinka
# if [ $? != 0 ]
# then 
#     echo "ERROR: Installing adafruit-blinka"; exit 1
# fi



# Install Seed studio 
# Seeed studio is added as a git submodule of this repo
git submodule update --init
echo "Step 4: Install Seeed studio voice card"
cd ../seeed-voicecard/ #change directory to seeed voice card. 
echo $PWD
sudo ./install.sh
if [ $? != 0 ]
then 
    echo "ERROR: Installing SeedStudio voice card"; exit 1
fi
cd - #change directory back

#Pass path to the all the services to daemon script.
echo "Step 3: Setting up system daemons script"
sudo ./daemons.sh "$USER/thegoodwand/services"
if [ $? != 0 ]
then 
    echo "ERROR: Running Deamon script"; exit 1
fi