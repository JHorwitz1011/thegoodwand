import time
import board
import digitalio

print("press the button!")

button = digitalio.DigitalInOut(board.D26)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

while True:
    print(button.value) # light when button is pressed!
