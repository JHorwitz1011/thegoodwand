echo "Turning Off Samsung Frame"
ir-ctl -d /dev/lirc0 --send=samframe.txt
echo "Turning Off LG TVs"
ir-ctl -d /dev/lirc0 --send=lg.txt
echo "Turning Off SONY TVs"
ir-ctl -d /dev/lirc0 --send=sony.txt
echo "Turning Off Samsung TVs"

