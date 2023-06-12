from bq24296M import bq24296M
import time, sys, getopt


CLI_HELP = """
Usage: python bq24296M.py [OPTIONS]
    
Options: 
    -r <register>                           read a register in hex, ex "-r 1" 
    -w <Register,Value>                     write to a register in hex, ex "-w 0,0f"
    -d                                      dump contents of all registers
    --power_off                             powers off device.
    --status                                prints system status
    --faults                                prints new system faults"""

# System status strings
class StatusStrings:
    VBUS_STATUS_STR = ["Unknown", "USB Host", "Adapter Port", "OTG"]
    CHRG_STATUS_STR = ["Not Charging", "Pre Charge", "Fast Charging", "Charge Done"]
    DPM_STATUS_STR = ["Not DPM", "In dynamic power management. Source Overloaded"]
    PG_STATUS_STR = ["Not Good Power", "Power Good"]
    THERM_STATUS_STR = ["Normal", "In Thermal Regulation"]
    VSYS_STATUS_STR = ["Not in VSYSMIN regulation (BAT > VSYSMIN)", "In VSYSMIN regulation (BAT < VSYSMIN)"]

#fault strings
class FaultStrings:
    WATCHDOG_FAULT = ["Normal", "Watchdog timer expired"]
    OTG_FAULT = ["Normal", "VBUS overloaded in OTG, or VBUS OVP, or battery is too low"]
    CHRG_FAULT = ["Normal", "Input fault","Thermal Shutdown", "Charge timer expired"]
    BAT_FAULT = ["Normal", "Battery OVP"]
    NTC_FAULT = ["Normal", "Hot", "Cold", "hot cold"]



def formatVal(val):
    hex_val = '{0:02x}'.format(val)
    bin = '{0:08b}'.format(val)
    return hex_val, bin


def cli_print_reg(reg,val):
    hex_val , bin = formatVal(val)
    reg_s = '{0:02x}'.format(reg)
    print(f"[REG 0x{reg_s}]: 0x{hex_val} | 0b{bin}")


def cli_dump_registers():
    for reg in range(charger.NUM_REG+1):
        cli_print_reg(reg,charger._readByte(reg))
        
def cli_write_reg(opt,arg):
    args = arg.split(',')
    
    if len(args) != 2: 
        print(f"[Write] Invalid argument length. Expecting 2, recived {len(args)}\n\n{CLI_HELP}")
        return
    
    else:
        try:
            reg = int(args[0], 16)
            val = int(args[1],16)
            
        except:
            print("[Write] Invalid format")
            return
    
        if (reg > charger.NUM_REG) or (val > 0xff):
            print("[Write] Invalid value size")
        else:
            charger._writeByte(reg, val)
            cli_read_reg(hex(reg))


def cli_read_reg(args):
    try:
        reg = int(args,16)
    except: 
        print("[READ] Invalid format")
        return
    if reg <= charger.NUM_REG:
        cli_print_reg(reg,charger._readByte(reg))
    
    else:
        print(f"[READ] Invalid Register\n{CLI_HELP}")

def cli_system_status():
    status = charger.getSystemStatus()
    print(f"[VBUS  STATUS] {StatusStrings.VBUS_STATUS_STR[(status & charger.VBUS_STAT_MASK) >> charger.VBUS_STAT_SHIFT]}")
    print(f"[CHAR  STATUS] {StatusStrings.CHRG_STATUS_STR[(status & charger.CHRG_STAT_MASK) >> charger.CHRG_STAT_SHIFT]}")
    print(f"[DPM   STATUS] {StatusStrings.DPM_STATUS_STR[(status & charger.DPM_STAT_MASK) >> charger.DPM_STAT_SHIFT]}")
    print(f"[PG    STATUS] {StatusStrings.PG_STATUS_STR[(status & charger.PG_STAT_MASK) >> charger.PG_STAT_SHIFT]}")
    print(f"[THERM STATUS] {StatusStrings.THERM_STATUS_STR[(status & charger.THERM_STAT_MASK) >> charger.THERM_STAT_SHIFT]}")
    print(f"[VSYS  STATUS] {StatusStrings.VSYS_STATUS_STR[(status & charger.VSYS_STAT_MASK) >> charger.VSYS_STAT_SHIFT]}")

def cli_system_faults():
    faults = charger.getNewFaults()
    print(f"[WATCHDOG FAULT] {FaultStrings.WATCHDOG_FAULT[(faults & charger.WATCHDOG_FAULT_MASK) >> charger.WATCHDOG_FAULT_SHIFT]}")
    print(f"[OTG      FAULT] {FaultStrings.OTG_FAULT[(faults & charger.OTG_FAULT_MASK) >> charger.OTG_FAULT_SHIFT]}")
    print(f"[CHRG     FAULT] {FaultStrings.CHRG_FAULT[(faults & charger.CHRG_FAULT_MASK) >> charger.CHRG_FAULT_SHIFT]}")
    print(f"[BAT      FAULT] {FaultStrings.BAT_FAULT[(faults & charger.BAT_FAULT_MASK) >> charger.BAT_FAULT_SHIFT]}")
    print(f"[NTC      FAULT] {FaultStrings.NTC_FAULT[(faults & charger.NTC_FAULT_MASK) >> charger.NTC_FAULT_SHIFT]}")


def cli_main_args(argv):
    try:
        opts, args = getopt.getopt(argv, 'hdr:w:', ["power_off","help","status","faults"])
    except:
        print("[ARGS] INVALID OPTIONS")
        print(CLI_HELP)
        return
    for opt, args in opts:
        if opt == '-h':
            print(CLI_HELP)
        
        elif opt == '-r':
            cli_read_reg(args)
        
        elif opt == '-w':
            cli_write_reg(opts,args)

        elif opt == '-d':
            cli_dump_registers()
        
        elif opt == '--status':
            cli_system_status()
        
        elif opt == '--faults':
            cli_system_faults()
        
        elif opt == '--power_off':
            print("Powering off...")
            charger.powerDown()
        
        elif opt == '--help':
            print(CLI_HELP)
        
        else:
            print("[ARGS] Unknown command")



if __name__ == "__main__":
    
    argv = sys.argv[1:]
    charger = bq24296M()

    cli_main_args(argv)
