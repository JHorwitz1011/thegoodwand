#ifndef WS2812SERVICE_H
#define WS2812SERVICE_H

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <signal.h>
#include <stdarg.h>
#include <getopt.h>
#include <string>
#include <queue>

#include "rpi_ws281x/clk.h"
#include "rpi_ws281x/gpio.h"
#include "rpi_ws281x/dma.h"
#include "rpi_ws281x/pwm.h"
#include "rpi_ws281x/ws2811.h"

//ws2812 settings
#define PWM_CHANNEL             0
#define TARGET_FREQ             WS2811_TARGET_FREQ
#define GPIO_PIN                12
#define DMA                     10
#define STRIP_TYPE              WS2812_STRIP
#define LED_COUNT               21
#define FULL_BRIGHTNESS         255
#define HALF_BRIGHTNESS         127
#define GAMMA_CORRECTION        1.8

//frame data
#define SEC_IN_MICROSECONDS 	1000000
#define FPS 					60
#define DISPLAY_PERIOD 			SEC_IN_MICROSECONDS/FPS

//manipulation mask
#define BITS_IN_BYTE            8
#define RED_SHIFT               sizeof(uint8_t)*2*BITS_IN_BYTE
#define GREEN_SHIFT             sizeof(uint8_t)*BITS_IN_BYTE
#define BLUE_SHIFT              0
#define RED_MASK			    0x00FF0000
#define GREEN_MASK 			    0x0000FF00
#define BLUE_MASK 			    0x000000FF

// indice parsing 
#define indicatorIndex 0

//heartbeat defaults
#define DEFAULT_MIN_BRIGHTNESS  0
#define DEFAULT_MAX_BRIGHTNESS  255
#define DEFAULT_RAMP_TIME       500000
#define DEFAULT_DELAY           500000

//data types
enum systemAnimations {block, raw, animation, equalizer, heartbeat, fire, none};
enum indicatorAnimations {off, solid, pulse};

typedef struct RgbColor {
    uint8_t r;
    uint8_t g;
    uint8_t b;
} RgbColor;

typedef struct HsvColor {
    uint8_t h;
    uint8_t s;
    uint8_t v;
} HsvColor;

class WS2812Service {
    public:
        bool clearOnExit;
        ws2811_t ledstring;
        ws2811_led_t* strip;
        static bool running;
        bool emptyLightbar;
        ws2811_return_t ret;            //return value for ws281x calls

        uint64_t frameStart;
        uint64_t frameDuration;
        uint64_t timeFramePostRender;
        uint64_t timeFramePreRender;

        //heartbeat control
        uint8_t hbLBMinBrightness;
        uint8_t hbLBMaxBrightness;
        uint32_t hbLBRampTime;
        uint32_t hbLBDelay;

        uint8_t hbMLMinBrightness;
        uint8_t hbMLMaxBrightness;
        uint32_t hbMLRampTime;
        uint32_t hbMLDelay;

        //fire
        uint8_t fireTargetBrightness[20];
        uint8_t fireActualBrightness[20];
        int fireFramesUntilUpdate;
        int fireDeltaBrightness;

        //default lightbar colors
        systemAnimations defaultAnimation;
        HsvColor defaultColorHSV;
        RgbColor defaultColorRGB;

        //indicator lights
        indicatorAnimations indicatorState;
        HsvColor indicatorColorHSV;                
        RgbColor indicatorColorRGB;                

        //csv stuff
        std::queue<std::vector<ws2811_led_t>> colorData;
	    std::queue<int> timeData;
        
        WS2812Service();
        // ~WS2812Service();

        void stripRender();
        void drawLightbarFill(uint8_t r, uint8_t g, uint8_t b);
        void drawLightbarFill(uint32_t rgb);
        void drawLightbar();
        void drawIndicator();
        void stripClear();
        void stripSet(int index, uint8_t r, uint8_t g, uint8_t b);
        void stripSet(int index, uint32_t rgb);
        void printStrip();
        void run();

        //csv
        void loadCSVAnimation(std::string filepath);
        void drawFrame();
        void clearAnimation();
        void clearFire();

        //built-in states 
        void drawLightbarHeartbeat();
        void drawIndicatorHeartbeat();
        void drawLightbarFire();
        void drawLightbarEqualizer();

        //helper functions for default color states
        void setIndicatorColorRGB(uint8_t r, uint8_t g, uint8_t b);
        void setIndicatorColorHSV(uint8_t h, uint8_t s, uint8_t v);
        void setDefaultColorRGB(uint8_t r, uint8_t g, uint8_t b);
        void setDefaultColorHSV(uint8_t h, uint8_t s, uint8_t v);

        void setIndicatorColorRGB(ws2811_led_t color);
        void setIndicatorColorHSV(ws2811_led_t color);
        void setDefaultColorRGB(ws2811_led_t color);
        void setDefaultColorHSV(ws2811_led_t color);

        HsvColor hsvHexToStruct(ws2811_led_t hex);
        RgbColor rgbHexToStruct(ws2811_led_t hex);
        ws2811_led_t rgbColorToWS2811_LED_T(RgbColor color);
        ws2811_led_t hsvColorToWS2811_LED_T(HsvColor color);

        void initializeWS2812();
        const uint8_t designToHardwareMap[LED_COUNT - 1] = {1, 20, 2, 19, 3, 18, 4, 17, 5, 16, 6, 15, 7, 14, 8, 13, 9, 12, 10, 11}; //translates csv index to hardware index of strip

    private:
        ws2811_led_t heartbeatLED(HsvColor color, uint8_t minBrightness, uint8_t maxBrightness, uint32_t rampTime, uint32_t delay);


        bool isValidFilepath();
        void setupHandlers();
        uint64_t micros();
        RgbColor hsvToRGB(HsvColor hsv);

        HsvColor rgbToHSV(RgbColor rgb);
};

#endif