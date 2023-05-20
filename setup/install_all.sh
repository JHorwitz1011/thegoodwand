#1bin/sh

if [ $USER = "root" ]
then 
    echo "[ERROR: install_all.sh $LINENO] Do not run as SUDO"
    exit 1
fi

echo "Starting TGW Setup."
echo "Step 1: update and upgrade the system"

sudo apt-get update
if [ $? != 0 ]
then 
    echo "[ERROR: install_all.sh $LINENO] Updating packages"; exit 1
fi

# Required packages 
    # python3-pip
    # python3-smbus
    # mosquitto
    # mosquitto-clients
    # supervisor
    # ndeflib
    # paho-mqtt
    # sysstat

echo "Step 2: Install required pachages"

sudo apt-get install python3-pip
if [ $? != 0 ]
then 
    echo "[ERROR: install_all.sh $LINENO] Installing PIP"; exit 1
fi

sudo apt-get install python3-smbus
if [ $? != 0 ]
then 
    echo "[ERROR: install_all.sh $LINENO] Installing SMBUS"; exit 1
fi

sudo apt-get install -y mosquitto
if [ $? != 0 ]
then 
    echo "[ERROR: install_all.sh $LINENO] Installing Mosquitto"; exit 1
fi

sudo apt-get install -y mosquitto-clients
if [ $? != 0 ]
then 
    echo "[ERROR: install_all.sh $LINENO] Installing Mosquitto Client"; exit 1
fi

sudo apt install -y vlc
if [ $? != 0 ]
then 
    echo "[ERROR: install_all.sh $LINENO] Installing VLC"; exit 1
fi

sudo apt-get install alsa-base pulseaudio
if [ $? != 0 ]
then 
    echo "[ERROR: install_all.sh $LINENO] Installing alsa-base pulseaudio Client"; exit 1
fi

echo "Step 3: Install Supervisor"
sudo apt-get install -y supervisor
echo "SUPERVISOR $?"
if [ $? != 0 ]
then 
    echo "[ERROR: install_all.sh $LINENO] Installing Supervisor"; exit 1
fi

sudo pip3 install ndeflib
if [ $? != 0 ]
then 
    echo "[ERROR: install_all.sh $LINENO] Installing NDEFLIB"; exit 1
fi

sudo pip3 install paho-mqtt
if [ $? != 0 ]
then 
    echo "[ERROR: install_all.sh $LINENO] Installing paho-mqtt"; exit 1
fi

sudo apt-get install -y sysstat
if [ $? != 0 ]
then 
    echo "[ERROR: install_all.sh $LINENO] Installing sysstat"; exit 1
fi

sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
if [ $? != 0 ]
then 
    echo "[ERROR: install_all.sh $LINENO] Installing adafruit-circuitpython-neopixel"; exit 1
fi

sudo python3 -m pip install --force-reinstall adafruit-blinka
if [ $? != 0 ]
then 
    echo "[ERROR: install_all.sh $LINENO] Installing adafruit-blinka"; exit 1
fi

sudo pip3 install python-vlc
if [ $? != 0 ]
then 
    echo "[ERROR: install_all.sh $LINENO] Installing python-vlc"; exit 1
fi


# Install Seed studio 
# Seeed studio is added as a git submodule of this repo
git submodule update --init
echo "Step 4: Install Seeed studio voice card"
cd ../seeed-voicecard/ #change directory to seeed voice card. 
sudo ./install.sh
if [ $? != 0 ]
then 
    echo "[ERROR: install_all.sh $LINENO] Installing SeedStudio voice card"; exit 1
fi
cd - #change directory back

# Add temp files to bashrc

if grep -Fq "export PATH=~/thegoodwand/templates:" ~/.bashrc
then 
    echo "Templates already added to ./bashrc"
else
    echo "Adding template to path" 
    echo "export PATH="~/thegoodwand/templates:$PATH"" > temp
    cat temp >> ~/.bashrc
    rm temp
fi

if grep -Fq "enable_uart=1" /boot/config.txt
then
        echo "Uart Already enabled"
else
    echo "enable_uart=1" | sudo tee -a /boot/config.txt
fi

echo "Updating IR Pins"
sudo sed -i 's/#dtoverlay=gpio-ir,gpio_pin=17/dtoverlay=gpio-ir,gpio_pin=23/g' /boot/config.txt
sudo sed -i 's/#dtoverlay=gpio-ir-tx,gpio_pin=18/dtoverlay=gpio-ir,gpio_pin=22/g' /boot/config.txt

#Pass path to the all the services to daemon script.
echo "Step 3: Setting up system daemons script"
sudo ./daemons.sh "$USER/thegoodwand/services" $USER
if [ $? != 0 ]
then 
    echo "[ERROR: install_all.sh $LINENO] Running Deamon script"; exit 1
fi

sudo reboot now
