# Install script for directory: /home/tgw/thegoodwand/services/lights/rpi_ws281x

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Debug")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "/home/tgw/thegoodwand/services/lights/build/rpi_ws281x/libws2811.a")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/ws2811" TYPE FILE FILES
    "/home/tgw/thegoodwand/services/lights/rpi_ws281x/ws2811.h"
    "/home/tgw/thegoodwand/services/lights/rpi_ws281x/rpihw.h"
    "/home/tgw/thegoodwand/services/lights/rpi_ws281x/pwm.h"
    "/home/tgw/thegoodwand/services/lights/rpi_ws281x/clk.h"
    "/home/tgw/thegoodwand/services/lights/rpi_ws281x/dma.h"
    "/home/tgw/thegoodwand/services/lights/rpi_ws281x/gpio.h"
    "/home/tgw/thegoodwand/services/lights/rpi_ws281x/mailbox.h"
    "/home/tgw/thegoodwand/services/lights/rpi_ws281x/pcm.h"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/pkgconfig" TYPE FILE FILES "/home/tgw/thegoodwand/services/lights/build/rpi_ws281x/libws2811.pc")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  execute_process(COMMAND /sbin/ldconfig
                              RESULT_VARIABLE EXIT_STATUS
                              ERROR_QUIET)
             if (NOT EXIT_STATUS EQUAL 0)
                 message("Warning: Could not run ldconfig. You may need to manually run ldconfig as root to cache the newly installed libraries.")
             endif()
endif()

