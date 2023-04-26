echo "installing neopixel dependencies..."
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
sudo python3 -m pip install --force-reinstall adafruit-blinka

echo "installing mosquitto..."
sudo apt install -y mosquitto

echo "mosquitto debug:"
sudo systemctl status mosquitto

echo "mosquitto cmd line clients..."
sudo apt install -y mosquitto-clients

echo "installing mqtt python client..."
pip3 install paho-mqtt