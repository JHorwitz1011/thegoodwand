from FWLightAnimation import FWLightAnimation
import csv
import time

class FWCSV(FWLightAnimation):
    def __init__(self, filepath):
        self.animation = []

        file = open(filepath, newline='')
        for row in csv.reader(file, delimiter=',', quotechar='|'):
            self.animation.append(row)

        self.lengths = []
        for a in self.animation:
            self.lengths.append(float(a[0])/1000)
        print(self.lengths)
        self.currentAnimation = []
        self.currentRow = 0
        self.frameStart = -1
        # print(self.animation[0])


    def update(self, pixels):
        currentTime = time.time()

        if self.frameStart == -1:
            self.frameStart = currentTime

        while True:
            while(self._nextFrame()):  
                print(len(self.currentAnimation), self.currentAnimation, self.currentRow)
                for i in range(len(self.currentAnimation)):
                    pixels[i] = self.hexStringToTuple(self.currentAnimation[i])
                pixels.show()
                time.sleep(self.lengths[self.currentRow-1])
            self.currentAnimation = []
            self.currentRow = 0

    def hexStringToTuple(self, str):
        r = str[1:3]
        g = str[3:5]
        b = str[5:7]
        return (int(r, 16), int(g, 16), int(b, 16))
    def _nextFrame(self):
        if self.currentRow < len(self.animation):
            self.frameStart = time.time()
            self.currentAnimation = self.animation[self.currentRow][1:]
            self.currentRow += 1

            return True
        else:
            return False