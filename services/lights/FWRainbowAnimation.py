from FWLightAnimation import FWLightAnimation
import time
from constants import *

class FWRainbowAnimation(FWLightAnimation):
    def __init__(self, speed=.001):
        self.speed = speed

    def _wheel(self, pos):
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
        return (r, g, b)


    def _rainbow_cycle(self, pixels):
        for j in range(255):
            for i in range(NUM_LEDS):
                pixel_index = (i * 256 // NUM_LEDS) + j
                pixels[i] = self._wheel(pixel_index & 255)
            time.sleep(self.speed)
            pixels.show()

    def update(self, pixels):
        self._rainbow_cycle(pixels)
