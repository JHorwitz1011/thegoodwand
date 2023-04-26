# Lighting Architecture #

More info about ws2812 LEDs can be found here:

* [Datasheet](https://cdn-shop.adafruit.com/datasheets/WS2812.pdf)
* [Adafruit Tutorial 1](https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage)
* [Adafruit Neopixel Uber Guide](https://learn.adafruit.com/adafruit-neopixel-uberguide/the-magic-of-neopixels)

Important points:

* They're powered by 5v logic so you need a level shifter somewhere to convert b/ 3.3v logic on the pi

I use some advanced-ish python stuff here. so if you're confused check out these links:

* [default params](https://www.geeksforgeeks.org/default-arguments-in-python/)
* [soft typing in python](https://docs.python.org/3/library/typing.html)

## Modularization Goal ##
We need a quick way to create animations in a reproducable pattern that doesn't clog up the code in other aspects of the project. Ideally, its a one-liner that initializes the lights, and one line to change the color. 

Here's my proposed solution:

## Lights Architecture v0 ##
Implemented in Python. relies on:

* [queue](https://docs.python.org/3/library/queue.html)
* [threading](https://docs.python.org/3/library/threading.html)
* [neopixel](https://docs.circuitpython.org/projects/neopixel/en/latest/)
* [Adafruit-Blinka](https://docs.circuitpython.org/projects/blinka/en/latest/)

### 1. FWLights ###

> overall system that manages and runs animations.

public members:

```python
__init__(pin, order='RGB' numLEDS=10) -> bool
```

||initializes light module and resets all color to none|
|--|--|
|**pin**| gpio pin to send data|
|**order**|order of lights. important bc if we switch light manufacturer sometimes its backwards.|
|**numLEDS**|number of LEDs on the chain. important for scrolling animation speed. also allows us to change density of lights without breaking the code.|
|**spacing:**| distance in mm spacing between lights? for scrolling animation speed, etc.. idk we'd have to think about it.|
|return|false if something fails true otherwise|

```python
run_and_loop_forever(queue: queue, fs=60) -> None
```

||blocks on a new thread, listening for new animation objects on the queue at the given sample rate.|
|--|--|
|**queue**| pointer to queue object (allows animations to be passed in between |
|**fs**|maximum sampling rate at which LEDs are updated and queue is checked.|

private members:

```python
update_leds(animation: FWLightAnimation) -> bool
```

||attempts to update LEDs based on given annimation object |
|--|--|
|**animation**| custom object described below... holds timing info regarding when animation should be played and pointer to animation object |
|return | true if animation was valid and able to play, false otherwise|

### 2. FWLightAnimation ###

>super class for animation data. allows us and developers to easily create custom animations.
>
>basic functionality is that  `__init__` describes when the animation can be played, and `update` describes how the lights update. FWLightAnimation acts as a superclass. Developers or us will override `update(t)` w/ the animation data.

```python
__init__(numLEDS: int, spacing: float, loop: int, startTime: float, endTime: float) -> None
```

||creates an animation object |
|--|--|
|**numLEDS** | leds on the strip|
|**spacing** | spacing between lights on the strip |
|**loop**| how many times animation repeats|
|**startTime** | time (type still unsure maybe since epoch idk) animation starts |
|**endTime** | time (type still unsure maybe since epoch idk) animation ends |

```python
@abstractmethod
update(t: float) -> tuple(tuple(int,int,int))
```

||calculates light value output based on arbitrary time value t |
|--|--|
|**t** | current time as float (type still needs work. float is bad) |
|return | tuple of length `self.numLEDS`, each element is a tuple w/ 3 ints for color value |




### V0 Thoughts ###

Pros:

* easy to implement
* animations are modularized

Cons:

* only one application can control light animations at a time. If we're running multiple scripts in different languages it just doesn't work...
* applicataion HAS to be coded in python

### V1 Brainstorming ###

* Socket-based C++ implementation is probably the ultimate solution
    * sockets allow the animation side of it all to be very fast and efficient
    * all animation classes could be developed in C++
    * master file for all animation data, need some kind of identifier for all animations (especially when we get devlopers making and implementing their own... install process required?)
    * script would listen on a port locally for a packet we would design - allowing ANY application in ANY language to write animations.


    I didn't want to bother writing it out bc V0 will work for now.
