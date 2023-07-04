
from dataclasses import dataclass

@dataclass
class Faults:
    watchdog:bool           = False
    otg:bool                = False
    input:bool              = False
    thermal_shutdown:bool   = False
    charge_timer:bool       = False
    battery:bool            = False
    hot:bool                = False
    cold:bool               = False


def set_faults() -> Faults:
    faults = Faults
    faults.charge_timer = True
    return faults

def print_faults(faults:Faults) -> None:
    print(faults.watchdog)
    print(faults.otg)
    print(faults.input)
    print(faults.thermal_shutdown)
    print(faults.charge_timer)
    print(faults.battery)
    print(faults.hot)
    print(faults.cold)\
    
faults:Faults = set_faults()

print(faults.charge_timer)