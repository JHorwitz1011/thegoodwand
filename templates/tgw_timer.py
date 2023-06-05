import threading

class tgw_timer():

    def __init__(self, interval, function, args=[], kwargs={}, name=""):
        self._interval = interval
        self._function = function
        self._args = args
        self._kwargs = kwargs
        self.timer = None
        self.timer_name = name
        self.lights = None
        self.audio = None

    def start(self):
        if self._interval != 0:
            self.timer = threading.Timer(self._interval, self._function, self._args, self._kwargs)
            self.timer.setName(self.timer_name)
            self.timer.start()
        pass

    def stop(self):
        try:
            #logger.debug(f"Timer Canceled {self.timer.getName()}")
            self.timer.cancel()
        except Exception as e:
            pass
            #logger.warning(f"cancel timer error {e}")
 

    def is_alive(self):
        try: 
            if self.timer.is_alive():
                return True
            else:
                return False
        except Exception as e:
            #logger.warning(f"is alive exception {e}")
            return False 