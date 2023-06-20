cmake_minimum_required(VERSION 3.9.1)

project(TGWLightService)

# General project stuff
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_BUILD_TYPE Debug)
add_compile_definitions(ASSETS="${CMAKE_SOURCE_DIR}/assets")
add_definitions(-w)

# Dependency of rpi_ws281x and mqtt
find_package(Threads REQUIRED)

# rpi_ws281x
add_subdirectory(rpi_ws281x)

# json
set(JSON_BuildTests OFF CACHE INTERNAL "")
add_subdirectory(json)

# MQTT
# Paho MQTT C++
set(PAHO_MQTT_CPP_INCLUDE_DIR "$ENV{HOME}/thegoodwand/libraries/paho.mqtt.cpp/src")
set(PAHO_MQTT_CPP_LIB_DIR "$ENV{HOME}/thegoodwand/libraries/paho.mqtt.cpp/build/src")
add_library(paho-mqttpp3 STATIC IMPORTED)
set_target_properties(paho-mqttpp3 PROPERTIES IMPORTED_LOCATION "${PAHO_MQTT_CPP_LIB_DIR}/libpaho-mqttpp3.a")

# Paho MQTT C
set(PAHO_MQTT_C_INCLUDE_DIR "$ENV{HOME}/thegoodwand/libraries/paho.mqtt.c/src")
set(PAHO_MQTT_C_LIB_DIR "$ENV{HOME}/thegoodwand/libraries/paho.mqtt.c/build/src")
add_library(paho-mqtt3a STATIC IMPORTED)
set_target_properties(paho-mqtt3a PROPERTIES IMPORTED_LOCATION "${PAHO_MQTT_C_LIB_DIR}/libpaho-mqtt3a.a")

# TGWLightService executable
add_executable(TGWLightService main.cpp WS2812Service.cpp)

# Link against the Paho MQTT C++ and C libraries
target_include_directories(TGWLightService PRIVATE ${PAHO_MQTT_CPP_INCLUDE_DIR} ${PAHO_MQTT_C_INCLUDE_DIR})

target_link_libraries(TGWLightService
    ws2811
    nlohmann_json::nlohmann_json
    ${CMAKE_THREAD_LIBS_INIT}
    ${CMAKE_DL_LIBS}
    paho-mqttpp3
    paho-mqtt3a
)
