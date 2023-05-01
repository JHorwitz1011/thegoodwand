from FWLights import FWLights
from FWCSV import FWCSV
from FWBlink import FWBlink
from FWRainbowAnimation import FWRainbowAnimation
import time

if __name__ == "__main__":
    testobj = FWLights(fs=60)
    asdf = FWCSV('test.csv')
    print('starting!')
    testobj.run_and_loop_forever()
    time.sleep(.1)
    testobj.light_queue.put(asdf)
    time.sleep(10)
    print('after loop!')
    testobj.close()
