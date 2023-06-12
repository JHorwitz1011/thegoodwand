#!/bin/bash

# Edit the boot config with needed settings 

sed -i '/hdmi_blanking/d' /boot/config.txt #delete existing 
echo 'hdmi_blanking=1' >> /boot/config.txt

sed -i '/dtoverlay=disable-bt/d' /boot/config.txt #delete existing 
echo "dtoverlay=disable-bt" >> /boot/config.txt

# Lower GPU memory
#sed -i 's/gpu_mem=[0-9]*/gpu_mem=16/' /boot/config.txt 

sed -i '/^#arm_freq=/s/^#//' /boot/config.txt  # Uncomment the frequency param. 
sed -i 's/^arm_freq=[0-9]*/arm_freq=600/' /boot/config.txt #change the frequecny to 600Mhz

sed -i '/enable_uart=1/d' /boot/config.txt
echo 'enable_uart=1' >> /boot/config.txt

# sed -i '/maxcpus/d' /boot/config.txt
# echo 'maxcpus=1' >> /boot/config.txt

sed -i 's/#dtoverlay=gpio-ir,gpio_pin=17/dtoverlay=gpio-ir,gpio_pin=23/g' /boot/config.txt
sed -i 's/#dtoverlay=gpio-ir-tx,gpio_pin=18/dtoverlay=gpio-ir,gpio_pin=22/g' /boot/config.txt

