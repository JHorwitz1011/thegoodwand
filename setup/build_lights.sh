echo "building lights libraries and service"

#paho mqtt C
cd ~/thegoodwand/libraries/paho.mqtt.c
rm -r build
mkdir build
cd build
cmake .. -DPAHO_BUILD_STATIC=TRUE -DPAHO_BUILD_SHARED=FALSE -DPAHO_WITH_SSL=FALSE -DPAHO_HIGH_PERFORMANCE=TRUE
make -j4

#paho mqtt C++
cd ~/thegoodwand/libraries/paho.mqtt.cpp
rm -r build
mkdir build
cd build
cmake .. -DPAHO_BUILD_STATIC=TRUE -DPAHO_BUILD_SHARED=FALSE -DPAHO_WITH_SSL=FALSE -DPAHO_HIGH_PERFORMANCE=TRUE
make -j4

#light service
cd ~/thegoodwand/services/lights
rm -r build
mkdir build
cd build
cmake ..
make -j4