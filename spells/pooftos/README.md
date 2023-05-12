#Install Instructions
#
# Step 1: setup the HW lines
# BEGIN ADDED
dtoverlay=gpio-ir,gpio_pin=23
dtoverlay=gpio-ir-tx,gpio_pin=22
# END ADDED
#
# Step 2: Get the Libraries
sudo apt-get install ir-keytable -y
#
#
# Step 3: Test: 
# Instructions are at: https://github.com/gordonturner/ControlKit/blob/master/Raspbian%20Setup%20and%20Configure%20IR.md
# Normally the ir receiver device is assigned to /sys/class/rc/rc0. However, due to the nature of multi threaded device probe, the receiver device can be assigned to /sys/class/rc/rc1.

lsmod | grep gpio
cat /proc/bus/input/devices
ir-keytable

#
# Dont use the linux lirc library which was deprecated in 2019, use gpio-ir, 
#
#
# USAGE
# To display rcvd RAW iR codes: 
 ir-ctl -d /dev/lirc1 -r 
 # To display processed codes with protocol:
# Enable all protocols:
sudo ir-keytable -p all -s rc0
# Capture with:
 ir-keytable -t -s rc0
 # Send sample captured with
 ir-ctl -d /dev/lirc0 --send=sony.txt
