#include <signal.h>
#include <stdexcept>
#include <sys/time.h>

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <queue>

#include "mqtt/async_client.h"
#include "WS2812Service.hpp"
#include "callback.hpp"

/**
 * initialize values
 */
bool WS2812Service::running = 0;

// WS2812Service::~WS2812Service() {
//     delete[] fireTargetBrightness;
//     delete[] fireActualBrightness;
// }

WS2812Service::WS2812Service() {
    

    this->clearOnExit = true;
    this->strip = (ws2811_led_t*)malloc(sizeof(ws2811_led_t) * LED_COUNT);
    this->frameStart = 0;

    //heartbeat
    hbLBMinBrightness = DEFAULT_MIN_BRIGHTNESS;
    hbLBMaxBrightness = DEFAULT_MAX_BRIGHTNESS;
    hbLBRampTime = DEFAULT_RAMP_TIME;
    hbLBDelay = DEFAULT_DELAY;

    hbMLMinBrightness = DEFAULT_MIN_BRIGHTNESS;
    hbMLMaxBrightness = DEFAULT_MAX_BRIGHTNESS;
    hbMLRampTime = DEFAULT_RAMP_TIME;
    hbMLDelay = DEFAULT_DELAY;

    //fire
    srand(time(NULL));
    // fireTargetBrightness = new uint8_t[20];
    // fireTargetBrightness = new uint8_t[20];
    fireFramesUntilUpdate = 0;
    fireDeltaBrightness = 1;

    //clear 
    this->defaultAnimation = none;
    this->defaultColorHSV = {};
    this->defaultColorRGB = {};
    this->indicatorColorHSV = {};
    this->indicatorColorRGB = {};

    this->frameDuration = 0;

    //initialize rgb struct
    this->ledstring = {};                   //clear junk data
    this->ledstring.freq                    = TARGET_FREQ;
    this->ledstring.dmanum                  = DMA;
    this->ledstring.channel[0].gpionum      = GPIO_PIN;
    this->ledstring.channel[0].invert       = 0;
    this->ledstring.channel[0].count        = LED_COUNT;
    this->ledstring.channel[0].strip_type   = STRIP_TYPE;
    this->ledstring.channel[0].brightness   = FULL_BRIGHTNESS;

    this->ledstring.channel[1].gpionum      = 0;
    this->ledstring.channel[1].invert       = 0;
    this->ledstring.channel[1].count        = 0;
    this->ledstring.channel[1].strip_type   = 0;
    this->ledstring.channel[1].brightness   = 0;
    ws2811_set_custom_gamma_factor(&ledstring, GAMMA_CORRECTION);        //gamma correction :O
}

void WS2812Service::initializeWS2812() {
    WS2812Service::running = true;
    setupHandlers();
    if ((ret = ws2811_init(&ledstring)) != WS2811_SUCCESS) {
            fprintf(stderr, "ws2811_init failed: %s\n", ws2811_get_return_t_str(ret));
            throw std::invalid_argument(" ");
    }
}


void WS2812Service::drawLightbar() {
    if(colorData.size() > 0) {                                          //csv animation is loaded
        if (timeFramePreRender - frameStart > frameDuration) {
            emptyLightbar = false;
            frameStart = timeFramePreRender;
            drawFrame();
        }
    }
    else if (defaultAnimation != none) {                                                        //if not, resort to default heartbeat/fire/solid
        if(defaultAnimation == block)
            drawLightbarFill(defaultColorRGB.r, defaultColorRGB.g, defaultColorRGB.b);
        else if(defaultAnimation == heartbeat)
            drawLightbarHeartbeat();
        else if(defaultAnimation == fire)
            drawLightbarFire();
        else if(defaultAnimation == equalizer)
            drawLightbarEqualizer();
    }
    else if (!emptyLightbar){                                                   //if default is set, clear strip and continue
        emptyLightbar = true;
        frameStart = 0;
        frameDuration = 0;
        stripClear();
        std::cout << "CLEARING" << std::endl;
    }
}

void WS2812Service::drawIndicator() {
    if(indicatorState == pulse)
        drawIndicatorHeartbeat();
}

void WS2812Service::run() {
    uint64_t    timePrevFrameMicros,
                frameDifference = 0;    

    mqtt::async_client cli(SERVER_ADDRESS, CLIENT_ID);
	mqtt::connect_options connOpts;
	callback cb(cli, connOpts, this);

    initializeWS2812();

    //setup and connect mqtt
	connOpts.set_clean_session(false);
	cli.set_callback(cb);
	try {
		std::cout << "Connecting to the MQTT server..." << std::flush;
		cli.connect(connOpts, nullptr, cb);
	}
	catch (const mqtt::exception& exc) {
		std::cerr << "\nERROR: Unable to connect to MQTT server: '"
			<< SERVER_ADDRESS << "'" << exc << std::endl;
	}

    std::string filepath = ASSETS;
    filepath += "/";
    filepath += "yes_confirmed.csv";
    loadCSVAnimation(filepath);

    while (WS2812Service::running) {
        timeFramePreRender = micros();

        //LIGHTBAR DISPLAY LOGIC
        drawLightbar();

        //INDICATOR LIGHT LOGIC
        drawIndicator();

        //render the frame
        stripRender();

        //push around time variables
        timePrevFrameMicros = timeFramePostRender;
        timeFramePostRender = micros();
        frameDifference = timeFramePostRender - timePrevFrameMicros;

        //sleep until next frame
        if(frameDifference < DISPLAY_PERIOD)
            usleep(DISPLAY_PERIOD - (long)frameDifference);
    }

    if (clearOnExit) {
		stripClear();
		stripRender();
	}

    ws2811_fini(&ledstring);
}

/**
 * sends colors to the hardware
 */
void WS2812Service::stripRender() {
    for(int i = 0; i < LED_COUNT; i++) {
		ledstring.channel[PWM_CHANNEL].leds[i] = this->strip[i];
    }
    if ((ret = ws2811_render(&ledstring)) != WS2811_SUCCESS) {
        fprintf(stderr, "ws2811_render failed: %s\n", ws2811_get_return_t_str(ret));
        WS2812Service::running = 0;
    }
}

/**
 * set the strip to full zeros (lights off)
 */
void WS2812Service::stripClear() {
	drawLightbarFill(0);    //clear lightbar
    stripSet(0, 0);         //also clear indicator
}

/**
 * set color of one pixel on the strip
 */
void WS2812Service::stripSet(int index, uint8_t r, uint8_t g, uint8_t b) {
	this->strip[index] =  (r<<RED_SHIFT) | (g<<GREEN_SHIFT) | (b<<BLUE_SHIFT);
}

void WS2812Service::stripSet(int index, uint32_t rgb) {
    this->strip[index] = rgb;
}

/**
 * fill strip to be one color   
 */
void WS2812Service::drawLightbarFill(uint8_t r, uint8_t g, uint8_t b) {
	for(int i = 1; i < LED_COUNT; i++) {
		stripSet(i, r, g, b);
	}
}
void WS2812Service::drawLightbarFill(uint32_t rgb) {
    for(int i = 1; i < LED_COUNT; i++) {
		stripSet(i, rgb);
	}
}

/**
 * dump strip contents to console
 */
void WS2812Service::printStrip() {
	for(int i = 0; i < LED_COUNT; i++) {
		printf("Index %i, RGB: %i\n", i, (this->strip[i]));
	}
}


// PRIVATE METHODS
/**
 * ensure service exits properly without leaking memory
 */
void ctrlCHandler(int signum)
{
	(void)(signum);
    WS2812Service::running = 0;
}

/**
 * properly route interrupt and terminate signals from os
 */
void WS2812Service::setupHandlers(void)
{
    signal(SIGINT, ctrlCHandler);
    signal(SIGTERM, ctrlCHandler);
}

uint64_t WS2812Service::micros() {
    struct timeval currentTime;
    gettimeofday(&currentTime, NULL);
    return currentTime.tv_sec * 1000000ULL + currentTime.tv_usec;
}

void WS2812Service::loadCSVAnimation(std::string filepath) {
	std::string line, word;
    std::vector<ws2811_led_t> row;
	std::fstream file (filepath, std::ios::in);

	if(file.is_open())
	{
		while(getline(file, line))
		{
			row.clear();
 
			std::stringstream str(line);

            bool first = false;
			while(getline(str, word, ',')) {
                if(!first) {
                    timeData.push(std::stoi(word, nullptr, 10));                //time value
                    first = true;
                }
                else
    				row.push_back(std::stoul(word.substr(1, 7), nullptr, 16));       //hex
            }
			colorData.push(row);
		}
	}
	else
		std::cout<<"Could not open the file\n";
}


void WS2812Service::drawFrame() {
    std::vector<ws2811_led_t> frame = colorData.front();
    frameDuration = timeData.front()*1000;
    colorData.pop();
    timeData.pop(); //TODO: DOES THIS CAUSE A MEMORY LEAK ERROR???

    for(int i = 0; i < frame.size(); i++) {
        strip[designToHardwareMap[i]] = frame[i];
    }
}

void WS2812Service::clearAnimation() {
    std::queue<int> empty1;
    std::swap(timeData, empty1);
    std::queue<std::vector<ws2811_led_t>> empty2;
    std::swap(colorData, empty2);
}

RgbColor WS2812Service::hsvToRGB(HsvColor hsv) {
    RgbColor rgb;
    uint8_t region, remainder, p, q, t;
    
    if (hsv.s == 0)
    {
        rgb.r = hsv.v;
        rgb.g = hsv.v;
        rgb.b = hsv.v;
        return rgb;
    }
    
    region = hsv.h / 43;
    remainder = (hsv.h - (region * 43)) * 6; 
    
    p = (hsv.v * (255 - hsv.s)) >> 8;
    q = (hsv.v * (255 - ((hsv.s * remainder) >> 8))) >> 8;
    t = (hsv.v * (255 - ((hsv.s * (255 - remainder)) >> 8))) >> 8;
    
    switch (region)
    {
        case 0:
            rgb.r = hsv.v; rgb.g = t; rgb.b = p;
            break;
        case 1:
            rgb.r = q; rgb.g = hsv.v; rgb.b = p;
            break;
        case 2:
            rgb.r = p; rgb.g = hsv.v; rgb.b = t;
            break;
        case 3:
            rgb.r = p; rgb.g = q; rgb.b = hsv.v;
            break;
        case 4:
            rgb.r = t; rgb.g = p; rgb.b = hsv.v;
            break;
        default:
            rgb.r = hsv.v; rgb.g = p; rgb.b = q;
            break;
    }
    
    return rgb;
}

HsvColor WS2812Service::rgbToHSV(RgbColor rgb)
{
    HsvColor hsv;
    uint8_t rgbMin, rgbMax;

    rgbMin = rgb.r < rgb.g ? (rgb.r < rgb.b ? rgb.r : rgb.b) : (rgb.g < rgb.b ? rgb.g : rgb.b);
    rgbMax = rgb.r > rgb.g ? (rgb.r > rgb.b ? rgb.r : rgb.b) : (rgb.g > rgb.b ? rgb.g : rgb.b);
    
    hsv.v = rgbMax;
    if (hsv.v == 0)
    {
        hsv.h = 0;
        hsv.s = 0;
        return hsv;
    }

    hsv.s = 255 * long(rgbMax - rgbMin) / hsv.v;
    if (hsv.s == 0)
    {
        hsv.h = 0;
        return hsv;
    }

    if (rgbMax == rgb.r)
        hsv.h = 0 + 43 * (rgb.g - rgb.b) / (rgbMax - rgbMin);
    else if (rgbMax == rgb.g)
        hsv.h = 85 + 43 * (rgb.b - rgb.r) / (rgbMax - rgbMin);
    else
        hsv.h = 171 + 43 * (rgb.r - rgb.g) / (rgbMax - rgbMin);

    return hsv;
}

void WS2812Service::setIndicatorColorRGB(uint8_t r, uint8_t g, uint8_t b) {
    indicatorColorRGB = {r,g,b};
    indicatorColorHSV = rgbToHSV(indicatorColorRGB);
}

void WS2812Service::setIndicatorColorHSV(uint8_t h, uint8_t s, uint8_t v) {
    indicatorColorHSV = {h,s,v};
    indicatorColorRGB = hsvToRGB(indicatorColorHSV);
}

void WS2812Service::setDefaultColorRGB(uint8_t r, uint8_t g, uint8_t b) {
    defaultColorRGB = {r,g,b};
    defaultColorHSV = rgbToHSV(defaultColorRGB);
}

void WS2812Service::setDefaultColorHSV(uint8_t h, uint8_t s, uint8_t v) {
    defaultColorHSV = {h,s,v};
    defaultColorRGB = hsvToRGB(defaultColorHSV);
}
//////////////////
void WS2812Service::setIndicatorColorRGB(ws2811_led_t color) {
    indicatorColorRGB = rgbHexToStruct(color);
    indicatorColorHSV = rgbToHSV(indicatorColorRGB);
}

void WS2812Service::setIndicatorColorHSV(ws2811_led_t color) {
    indicatorColorHSV = hsvHexToStruct(color);
    indicatorColorRGB = hsvToRGB(indicatorColorHSV);
}

void WS2812Service::setDefaultColorRGB(ws2811_led_t color) {
    defaultColorRGB = rgbHexToStruct(color);
    defaultColorHSV = rgbToHSV(defaultColorRGB);
}

void WS2812Service::setDefaultColorHSV(ws2811_led_t color) {
    defaultColorHSV = hsvHexToStruct(color);
    defaultColorRGB = hsvToRGB(defaultColorHSV);
}

ws2811_led_t WS2812Service::rgbColorToWS2811_LED_T(RgbColor color) {
    return color.r << RED_SHIFT | color.g << GREEN_SHIFT | color.b << BLUE_SHIFT;
}

ws2811_led_t WS2812Service::hsvColorToWS2811_LED_T(HsvColor color) {
    RgbColor convertedColor = hsvToRGB(color);
    return convertedColor.r << RED_SHIFT | convertedColor.g << GREEN_SHIFT | convertedColor.b << BLUE_SHIFT;
}



HsvColor WS2812Service::hsvHexToStruct(ws2811_led_t hex) {
    HsvColor colorConverter;
    colorConverter.h = (hex&RED_MASK) >> RED_SHIFT;
    colorConverter.s = (hex&GREEN_MASK) >> GREEN_SHIFT;
    colorConverter.v = (hex&BLUE_MASK);
    return colorConverter;
}

RgbColor WS2812Service::rgbHexToStruct(ws2811_led_t hex) {
    RgbColor colorConverter;
    colorConverter.r = (hex&RED_MASK) >> RED_SHIFT;
    colorConverter.g = (hex&GREEN_MASK) >> GREEN_SHIFT;
    colorConverter.b = (hex&BLUE_MASK);
    return colorConverter;
}

static void logValue(uint8_t value) {
        std::cout << (int)value << std::endl;
}

ws2811_led_t WS2812Service::heartbeatLED(HsvColor color, uint8_t minBrightness, uint8_t maxBrightness, uint32_t rampTime, uint32_t delay) {
    uint64_t animationPeriod = 2*(rampTime + delay);
    uint64_t currentTime = timeFramePreRender % animationPeriod;
    uint8_t brightnessRange = maxBrightness - minBrightness;

    if(currentTime <= rampTime) {
        color.v = brightnessRange*currentTime/rampTime + minBrightness;
        std::cout << "up" << "current time" << currentTime << "animation period " << animationPeriod << "max brightness" << int(maxBrightness) << "min brightness" << int(minBrightness) << "brightness range" << int(brightnessRange) << "ramp" << rampTime << "delay" << delay << "v";
        logValue(color.v);
        return hsvColorToWS2811_LED_T(color);
    }
    else if(currentTime <= rampTime + delay) {
        color.v = maxBrightness;
        std::cout << "top" << "current time" << currentTime << "animation period " << animationPeriod << "max brightness" << int(maxBrightness) << "min brightness" << int(minBrightness) << "brightness range" << int(brightnessRange) << "ramp" << rampTime << "delay" << delay << "v";
        logValue(color.v);
        return hsvColorToWS2811_LED_T(color);
    }
    else if(currentTime <= 2*rampTime + delay) {
        color.v = maxBrightness - brightnessRange*(currentTime-rampTime-delay)/rampTime; //scale ramp to timing. -1 for overflow protection
        std::cout << "down" << "current time" << currentTime << "animation period " << animationPeriod << "max brightness" << int(maxBrightness) << "min brightness" << int(minBrightness) << "brightness range" << int(brightnessRange) << "ramp" << rampTime << "delay" << delay << "v";
        logValue(color.v);
        return hsvColorToWS2811_LED_T(color);
    }
    else {
        color.v = minBrightness;
        std::cout << "bot" << "current time" << currentTime << "animation period " << animationPeriod << "max brightness" << int(maxBrightness) << "min brightness" << int(minBrightness) << "brightness range" << int(brightnessRange) << "ramp" << rampTime << "delay" << delay << "v";
        logValue(color.v);
        return hsvColorToWS2811_LED_T(color);
    }
}


void WS2812Service::drawLightbarHeartbeat() {
    drawLightbarFill(heartbeatLED(defaultColorHSV, hbLBMinBrightness, hbLBMaxBrightness, hbLBRampTime, hbLBDelay));
}

void WS2812Service::drawIndicatorHeartbeat() {
    stripSet(0, heartbeatLED(indicatorColorHSV, hbMLMinBrightness, hbMLMaxBrightness, hbMLRampTime, hbMLDelay));
}

void WS2812Service::drawLightbarFire() {
    //called on every frame
    if(fireFramesUntilUpdate <= 0) {
        //change targets to something new
        for(int i = 0; i < 6; i++) {
            fireTargetBrightness[rand()%20] = rand() % 150;
            // std::cout << (int)fireTargetBrightness[i] << " ";
        }

        //update counter
        fireFramesUntilUpdate = rand() % 25;
        // std::cout << "new update counter" << fireFramesUntilUpdate;
    }

    //decrement frames counter
    fireFramesUntilUpdate--;

    //temporary color data to manage flickering
    HsvColor temp;
    temp.h = defaultColorHSV.h;
    temp.s = defaultColorHSV.s;
    temp.v = 0;
    // std::cout << "actual brightness: ";
    for(int i = 0; i < 20; i++) {
        if(fireActualBrightness[i] > fireTargetBrightness[i]) {
            fireActualBrightness[i] -= rand()%fireDeltaBrightness;
        }
        else if(fireActualBrightness[i] < fireTargetBrightness[i]) {
            fireActualBrightness[i] += rand()%fireDeltaBrightness;
        }
        else{
            // std::cout << "target reached!" << std::endl;
        }
        temp.v = fireActualBrightness[i];
        stripSet(designToHardwareMap[i], hsvColorToWS2811_LED_T(temp));
    }
}

void WS2812Service::clearFire() {
    memset(fireActualBrightness, 0, sizeof(fireActualBrightness)/sizeof(fireActualBrightness[0]));
    memset(fireTargetBrightness, 0, sizeof(fireTargetBrightness)/sizeof(fireTargetBrightness[0]));
    fireDeltaBrightness = 0;
    fireFramesUntilUpdate = 0;
}

void WS2812Service::drawLightbarEqualizer() {}