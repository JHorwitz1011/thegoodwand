from FWLightAnimation import FWLightAnimation
import time

class FWBlink(FWLightAnimation):
    def __init__(self, onlen, offlen, red, green, blue):
        super().__init__()
        self.onlen = onlen
        self.offlen = offlen
        self.color = (red, green, blue)
        self.startTime = -1

    def update(self, pixels):
        if self.startTime == -1:
            self.startTime = time.time()
        
        currentTime = time.time()

        dt = currentTime - self.startTime
        period = self.onlen + self.offlen

        if dt%period <= self.offlen:
            pixels.fill(self.color)
        else:
            pixels.fill((0,0,0))