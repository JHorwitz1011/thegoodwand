import subprocess
from multiprocessing import Process

import sys
import os
sys.path.append(os.path.expanduser('~/thegoodwand/templates'))
from MQTTObject import MQTTObject

class Conductor(MQTTObject):
    def __init__(self):
        super().__init__()
    def subp():
        subprocess.run(['python3', "/home/tgw/spells/second_spell.py"])

    def switch_process():
        child_proc.terminate()


    if __name__ == "__main__":
        child_proc = Process(target=subp) 
        child_proc.start()
        #child_proc.join()
        #time.sleep(2)
        #print "in parent process after child process join"
        #print "the parent's parent process: %s" % (os.getppid())

print("idk man")