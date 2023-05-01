#multithreading
from queue import Queue
import threading
import time

#lights control
import board
import neopixel

#some constants
from constants import *

class FWLights:
    def __init__(self, fs=60, pin=board.D12, brightness=0.2, auto_write=False):
        
        self.light_queue = Queue()
        
        self.fs = fs
        self.run = True
        self.thread = None
        self.currentAnimation = None
        self.pixels = neopixel.NeoPixel(pin, NUM_LEDS)
    
    # run forever checking at rate fs, for now just printing out anything that arrives in the qwueue
    def run_and_loop_forever(self):
        self.thread = threading.Thread(target=self._loop)
        self.thread.start()

    def _loop(self):
        while self.run:
            if not self.light_queue.empty():
                self.currentAnimation = self.light_queue.get(timeout=1)
            
            if self.currentAnimation is not None:
                self.update_leds()
            else:
                print('waiting!')
            time.sleep(1/self.fs)

    def update_leds(self):
        self.currentAnimation.update(self.pixels) # update pixels obj with necessary light info
        self.pixels.show()


    def close(self):
        print('close call!')
        self.run = False
        self.thread.join()


    