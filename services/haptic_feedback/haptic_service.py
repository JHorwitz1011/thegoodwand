import RPi.GPIO as GPIO
from time import sleep
import math
import csv


class Haptic_Feedback:
   
    def __init__(self, PIN = 33 ):
        
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(PIN,GPIO.OUT)
        self.haptic_pwm = GPIO.PWM(PIN, 1000)

    # sawtooth: ramps the vibratior intensity up to the intensity limit then turns the vibrator off
    #   period: Time of 1 cycle
    #   duty_cycle: % on of period vibrator is on [0 - 100]
    #   Intensity: how strong the vibration is [0 - 100] 
    #   Cycles: how many times to repeate the pattern
    def sawtooth(self, period, intensity, cycles):
        if intensity > 100:
            intensity = 100    
        self.haptic_pwm.start(0)
        samples = 100
        delay = period/samples
        
        for cycle in range(cycles):
            for i in range(100):
                dc = math.floor(i *intensity/100)
                self.haptic_pwm.ChangeDutyCycle(i)
                sleep(delay)
        self.haptic_pwm.stop()


    # Pulse: pulses the vibratior in an on off repeating fasion.
    #   period: Time of 1 cycle
    #   duty_cycle: % on of period vibrator is on [0 - 100]
    #   Intensity: how strong the vibration is [0 - 100] 
    #   Cycles: how many times to repeate the pattern
    def pulse(self, period, duty_cycle, intensity, cycles):
        
        if intensity > 100:
            intensity = 100 

        TON = math.floor(period * duty_cycle)/100 
        TOFF = period - TON
        self.haptic_pwm.start(0)

        for cycle in range(cycles):
            self.haptic_pwm.ChangeDutyCycle(intensity)
            sleep(TON)
            self.haptic_pwm.ChangeDutyCycle(0)
            sleep(TOFF)
        self.haptic_pwm.stop()

    # custom: allow user to define a custom vibration pattern. 
    #   file_custom: a custom file. row: [intensity 0-100],[sleep time]
    def custom(self, file_custom):
        
        with open(file_custom, 'r') as file:
            reader = csv.reader(file)
            self.haptic_pwm.start(0)
            for row in reader:
                self.haptic_pwm.ChangeDutyCycle(int(row[0]))
                sleep(float(row[1])) 
        self.haptic_pwm.stop()
          

vib = Haptic_Feedback()
print("Saw tooth example")
vib.sawtooth(.75, 50, 5)
sleep(.5)
print("Pulse example")
vib.pulse(.25,25,100,5)
sleep(.5)
print("Custom CSV example")
vib.custom("custom_haptic.csv")