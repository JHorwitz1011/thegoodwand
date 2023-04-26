from abc import ABC, abstractmethod
import neopixel

display_to_hardware_adapter = {
    0:20,
    1:1,
    2:19,
    3:2,
    4:18,
    5:3,
    6:17,
    7:4,
    8:16,
    9:5,
    10:15,
    11:6,
    12:14,
    13:7,
    14:13,
    15:8,
    16:12,
    17:9,
    18:11,
    19:10,
}

class FWLightAnimation(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def update(self, pixels):
        pass

    def lightToBoardIndex(self, index):
        return display_to_hardware_adapter[index]
