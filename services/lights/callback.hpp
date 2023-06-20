#pragma once
#include <iostream>
#include <cstdlib>
#include <string>
#include <cstring>
#include <cctype>
#include <thread>
#include <chrono>
#include "mqtt/async_client.h"
#include "nlohmann/json.hpp"
#include "WS2812Service.hpp"

using json = nlohmann::json;

#define FORMAT_RAW "raw"
#define FORMAT_ANIMATION "animation"
#define FORMAT_HEARTBEAT "heartbeat"
#define FORMAT_FIRE "fire"
#define FORMAT_SOLID "solid"
#define FORMAT_NONE "none"

#define HSV_IDENTIFIER "hsv"
#define RGB_IDENTIFIER "rgb"

const std::string SERVER_ADDRESS("tcp://localhost:1883");
const std::string CLIENT_ID("TGWLightService");
const std::string LIGHTBAR_TOPIC("goodwand/ui/view/lightbar");
const std::string MAINLED_TOPIC("goodwand/ui/view/main_led");

const int	QOS = 1;
const int	N_RETRY_ATTEMPTS = 5;

inline bool isValidFilepath (const std::string& name) {
	struct stat buffer;   
	std::cout << name << (stat (name.c_str(), &buffer) == 0) << std::endl;
  	return (stat (name.c_str(), &buffer) == 0); 
}

/////////////////////////////////////////////////////////////////////////////

// Callbacks for the success or failures of requested actions.
// This could be used to initiate further action, but here we just log the
// results to the console.

class action_listener : public virtual mqtt::iaction_listener
{
	std::string name_;

	void on_failure(const mqtt::token& tok) override {
		std::cout << name_ << " failure";
		if (tok.get_message_id() != 0)
			std::cout << " for token: [" << tok.get_message_id() << "]" << std::endl;
		std::cout << std::endl;
	}

	void on_success(const mqtt::token& tok) override {
		std::cout << name_ << " success";
		if (tok.get_message_id() != 0)
			std::cout << " for token: [" << tok.get_message_id() << "]" << std::endl;
		auto top = tok.get_topics();
		if (top && !top->empty())
			std::cout << "\ttoken topic: '" << (*top)[0] << "', ..." << std::endl;
		std::cout << std::endl;
	}

public:
	action_listener(const std::string& name) : name_(name) {}
};

/////////////////////////////////////////////////////////////////////////////

/**
 * Local callback & listener class for use with the client connection.
 * This is primarily intended to receive messages, but it will also monitor
 * the connection to the broker. If the connection is lost, it will attempt
 * to restore the connection and re-subscribe to the topic.
 */
class callback : public virtual mqtt::callback,
					public virtual mqtt::iaction_listener

{
	// Counter for the number of connection retries
	int nretry_;
	// The MQTT client
	mqtt::async_client& cli_;
	// Options to use if we need to reconnect
	mqtt::connect_options& connOpts_;
	// An action listener to display the result of actions.
	action_listener subListener_;
    //light service object
    WS2812Service* lightService;
	// This deomonstrates manually reconnecting to the broker by calling
	// connect() again. This is a possibility for an application that keeps
	// a copy of it's original connect_options, or if the app wants to
	// reconnect with different options.
	// Another way this can be done manually, if using the same options, is
	// to just call the async_client::reconnect() method.
	void reconnect() {
		std::this_thread::sleep_for(std::chrono::milliseconds(2500));
		try {
			cli_.connect(connOpts_, nullptr, *this);
		}
		catch (const mqtt::exception& exc) {
			std::cerr << "Error: " << exc.what() << std::endl;
			exit(1);
		}
	}

	// Re-connection failure
	void on_failure(const mqtt::token& tok) override {
		std::cout << "Connection attempt failed" << std::endl;
		if (++nretry_ > N_RETRY_ATTEMPTS)
			exit(1);
		reconnect();
	}

	// (Re)connection success
	// Either this or connected() can be used for callbacks.
	void on_success(const mqtt::token& tok) override {}

	// (Re)connection success
	void connected(const std::string& cause) override {
		std::cout << "\nConnection success" << std::endl;
		cli_.subscribe(LIGHTBAR_TOPIC, QOS, nullptr, subListener_);		
		cli_.subscribe(MAINLED_TOPIC, QOS, nullptr, subListener_);
	}

	// Callback for when the connection is lost.
	// This will initiate the attempt to manually reconnect.
	void connection_lost(const std::string& cause) override {
		std::cout << "\nConnection lost" << std::endl;
		if (!cause.empty())
			std::cout << "\tcause: " << cause << std::endl;

		std::cout << "Reconnecting..." << std::endl;
		nretry_ = 0;
		reconnect();
	}

	// Callback for when a message arrives.
	void message_arrived(mqtt::const_message_ptr msg) override {
		std::cout << "Message arrived" << std::endl;
		std::cout << "\ttopic: '" << msg->get_topic() << "'" << std::endl;
		std::cout << "\tpayload: '" << msg->to_string() << "'\n" << std::endl;
        std::string topic = msg->get_topic();
        json payload;
        //attempt to parse
        bool parseSuccess = true;
        try
        {
             payload = json::parse(msg->to_string());
        }
        catch (json::parse_error& e)
        {
            parseSuccess = false;
        }

        if(parseSuccess) {
            if(topic == LIGHTBAR_TOPIC) {
                std::cout << "lightbar!" << std::endl;
                if(payload.contains("data")) {
                    json data = payload["data"];

                    if(data.contains("format")) {
                        std::string format = data["format"];

						//no more animation
						if(format == FORMAT_NONE) {
							lightService->defaultAnimation = none;
							lightService->drawLightbarFill(0);
							lightService->clearAnimation();
						}

						//raw  data
                        else if (format == FORMAT_RAW && data.contains("raw")) {
                            lightService->clearAnimation();
                            std::vector<ws2811_led_t> lights = data["raw"].get<std::vector<ws2811_led_t>>();
							for(int i = 0; i < lights.size(); i++) {
								if(data.contains("color_space") && data["color_space"] == HSV_IDENTIFIER) {
									lightService->stripSet(lightService->designToHardwareMap[i], lightService->hsvColorToWS2811_LED_T(lightService->hsvHexToStruct(lights[i]))); 
								}
								else {
									lightService->stripSet(lightService->designToHardwareMap[i], lights[i]);
								}
                            }
                        }

						//RGB default states
                        else if(!data.contains("color_space") || data["color_space"].get<std::string>() == RGB_IDENTIFIER) {
							if(format == FORMAT_SOLID) {
								lightService->clearAnimation();
								lightService->defaultAnimation = block;
								lightService->setDefaultColorRGB(data["color"].get<ws2811_led_t>());
							}
							else if(format == FORMAT_HEARTBEAT) {
								lightService->clearAnimation();
								lightService->defaultAnimation = heartbeat;
								lightService->setDefaultColorRGB(data["color"].get<ws2811_led_t>());
							}
							else if(format == FORMAT_FIRE) {
								lightService->clearAnimation();
								lightService->fireDeltaBrightness = 7;
								lightService->defaultAnimation = fire;
								lightService->setDefaultColorRGB(data["color"].get<ws2811_led_t>());
							}
                        }

						//HSV default states
                        else if(data.contains("color_space") || data["color_space"].get<std::string>() == HSV_IDENTIFIER) {
							if(format == FORMAT_SOLID) {
								lightService->clearAnimation();
								lightService->defaultAnimation = block;
								lightService->setDefaultColorHSV(data["color"].get<ws2811_led_t>());
							}
							else if(format == FORMAT_HEARTBEAT) {
								lightService->clearAnimation();
								lightService->defaultAnimation = heartbeat;
								if(data.contains("min_brightness"))
									lightService->hbLBMinBrightness = data["min_brightness"].get<uint8_t>();
								if(data.contains("max_brightness"))
									lightService->hbLBMaxBrightness = data["max_brightness"].get<uint8_t>();
								if(data.contains("ramp_time"))
									lightService->hbLBRampTime = data["ramp_time"].get<uint32_t>();
								if(data.contains("delay_time"))
									lightService->hbLBDelay = data["delay_time"].get<uint32_t>();
								lightService->setDefaultColorHSV(data["color"].get<ws2811_led_t>());
							}
							else if(format == FORMAT_FIRE) {
								lightService->clearAnimation();
								lightService->fireDeltaBrightness = 7;
								lightService->defaultAnimation = fire;
								lightService->setDefaultColorHSV(data["color"].get<ws2811_led_t>());
							}
                        }

						//CSV animations
                        if (format == FORMAT_ANIMATION) {
                                const std::string filepath = data["animation"];
								if(isValidFilepath(filepath)) {
									// absolute path
									std::cout << "ABSOLUTE PATH" << std::endl;
									lightService->loadCSVAnimation(filepath);
								}
								else {
									//try relative path to assets
									std::cout << "RELATIVE PATH" << std::endl;
									std::string filepath = ASSETS;
									filepath += "/";
									filepath += data["animation"];
									filepath += ".csv";
									std::cout << "loading " << filepath << std::endl;
									lightService->loadCSVAnimation(filepath);
								}

                        } 
                    }
                }
			}
            else if(topic == MAINLED_TOPIC) {
                std::cout << "mainled!" << std::endl;
				if(payload.contains("data")) {
					json data = payload["data"];
					if(data.contains("format")) {
                        std::string format = data["format"];

                        if(format == FORMAT_NONE) {
							lightService->setIndicatorColorRGB(0,0,0);
							lightService->indicatorState = off;
							lightService->stripSet(0, 0);
						}
						else if(!data.contains("color_space") || data["color_space"].get<std::string>() == RGB_IDENTIFIER) {
							if(format == FORMAT_HEARTBEAT) {
								lightService->indicatorState = pulse;
								lightService->setIndicatorColorRGB(data["color"].get<ws2811_led_t>());
							}
							else if(format == FORMAT_SOLID) {
								lightService->indicatorState = solid;
								lightService->setIndicatorColorRGB(data["color"].get<ws2811_led_t>());
								lightService->stripSet(0, lightService->indicatorColorRGB.r, lightService->indicatorColorRGB.g, lightService->indicatorColorRGB.b);
							}
						} 
						else if (data.contains("color_space") || data["color_space"].get<std::string>() == HSV_IDENTIFIER) {
							if(format == FORMAT_HEARTBEAT) {
								lightService->indicatorState = pulse;
								if(data.contains("min_brightness"))
									lightService->hbMLMinBrightness = data["min_brightness"].get<uint8_t>();
								if(data.contains("max_brightness"))
									lightService->hbMLMaxBrightness = data["max_brightness"].get<uint8_t>();
								if(data.contains("ramp_time"))
									lightService->hbMLRampTime = data["ramp_time"].get<uint32_t>();
								if(data.contains("delay_time"))
									lightService->hbMLDelay = data["delay_time"].get<uint32_t>();
								lightService->setIndicatorColorHSV(data["color"].get<ws2811_led_t>());
							}
							else if(format == FORMAT_SOLID) {
								lightService->indicatorState = solid;
								lightService->setIndicatorColorHSV(data["color"].get<ws2811_led_t>());
								lightService->stripSet(0, lightService->indicatorColorRGB.r, lightService->indicatorColorRGB.g, lightService->indicatorColorRGB.b);
							}
						}
					}
				}
            }
        }
	}

	void delivery_complete(mqtt::delivery_token_ptr token) override {}

public:
	callback(mqtt::async_client& cli, mqtt::connect_options& connOpts, WS2812Service* lightService)
				: nretry_(0), cli_(cli), connOpts_(connOpts), subListener_("Subscription"), lightService(lightService){}
};