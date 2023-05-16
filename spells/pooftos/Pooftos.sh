echo "Turning Off Samsung Frame"
ir-ctl -d /dev/lirc0 --send=$1/samframe.txt
echo "Turning Off LG TVs"
ir-ctl -d /dev/lirc0 --send=$1/lg.txt
echo "Turning Off SONY TVs"
ir-ctl -d /dev/lirc0 --send=$1/sony.txt
echo "Turning Off Samsung TVs"

