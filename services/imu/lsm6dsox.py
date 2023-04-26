import smbus
import RPi.GPIO as GPIO
from ctypes import c_int16
import time
import logging


#TODO refactor the I2C read, write and modify functions to combine the shub access switching

bus = smbus.SMBus(1)

SUCCESS = 0
ERROR   = -1
# Constants
GRAVITY = 9.81

LSM6DSOX_ADDRESS = 0x6A
LIS3MDL_ADDRESS   = 0x1C

INTERRUPT_1_PIN = 4
INTERRUPT_2_PIN = 17

WRITE = 0X00
READ  = 0X01

#REG FUNC_CFG_ACCESS (01h)
#SENSOR HUB ACCESS
FUN_SHUB_REG_ACCESS_SHIFT = 0X06
FUN_SHUB_REG_ACCESS_MASK  = 0X01 << FUN_SHUB_REG_ACCESS_SHIFT  
FUN_SHUB_ENABLE           = 0X01 << FUN_SHUB_REG_ACCESS_SHIFT
FUN_SHUB_DISABLE          = 0X00

# REG CTRL1_XL
CTRL1_XL_ODR_SHIFT       = 0x04
CTRL1_XL_ODR_MASK        = 0x0F << CTRL1_XL_ODR_SHIFT
CTRL1_XL_ODR_POWER_DOWN  = 0x00 << CTRL1_XL_ODR_SHIFT
CTRL1_XL_ODR_12_5_HZ     = 0x01 << CTRL1_XL_ODR_SHIFT
CTRL1_XL_ODR_26_HZ       = 0x02 << CTRL1_XL_ODR_SHIFT
CTRL1_XL_ODR_52_HZ       = 0x03 << CTRL1_XL_ODR_SHIFT
CTRL1_XL_ODR_104_HZ      = 0x04 << CTRL1_XL_ODR_SHIFT
CTRL1_XL_ODR_208_HZ      = 0x05 << CTRL1_XL_ODR_SHIFT
CTRL1_XL_ODR_416_HZ      = 0x06 << CTRL1_XL_ODR_SHIFT
CTRL1_XL_ODR_833_HZ      = 0x07 << CTRL1_XL_ODR_SHIFT
CTRL1_XL_ODR_1_66_KHZ    = 0x08 << CTRL1_XL_ODR_SHIFT
CTRL1_XL_ODR_3_33_KHZ    = 0x09 << CTRL1_XL_ODR_SHIFT
CTRL1_XL_ODR_6_66_KHZ    = 0x0A << CTRL1_XL_ODR_SHIFT

CTRL1_XL_SCALE_SHIFT     = 0x02
CTRL1_XL_SCALE_MASK      = 0x03 << CTRL1_XL_SCALE_SHIFT
CTRL1_XL_SCALE_2G        = 0x00 << CTRL1_XL_SCALE_SHIFT
CTRL1_XL_SCALE_4G        = 0x02 << CTRL1_XL_SCALE_SHIFT
CTRL1_XL_SCALE_8G        = 0x03 << CTRL1_XL_SCALE_SHIFT
CTRL1_XL_SCALE_16G       = 0x01 << CTRL1_XL_SCALE_SHIFT

CTRL1_XL_LPF2_XL_EN_SHIFT   = 0x01
CTRL1_XL_LPF2_XL_EN_MASK    = 0x01 << CTRL1_XL_LPF2_XL_EN_SHIFT
CTRL1_XL_LPF2_XL_ENABLE     = 0x01 << CTRL1_XL_LPF2_XL_EN_SHIFT
CTRL1_XL_LPF2_XL_DISENABLE  = 0x00 << CTRL1_XL_LPF2_XL_EN_SHIFT

# REG CTRL2_G
CTRL2_G_ODR_SHIFT       = 0x04
CTRL2_G_ODR_MASK        = 0x0F << CTRL2_G_ODR_SHIFT
CTRL2_G_ODR_POWER_DOWN  = 0x00 << CTRL2_G_ODR_SHIFT
CTRL2_G_ODR_12_5_HZ     = 0x01 << CTRL2_G_ODR_SHIFT
CTRL2_G_ODR_26_HZ       = 0x02 << CTRL2_G_ODR_SHIFT
CTRL2_G_ODR_52_HZ       = 0x03 << CTRL2_G_ODR_SHIFT
CTRL2_G_ODR_104_HZ      = 0x04 << CTRL2_G_ODR_SHIFT
CTRL2_G_ODR_208_HZ      = 0x05 << CTRL2_G_ODR_SHIFT
CTRL2_G_ODR_416_HZ      = 0x06 << CTRL2_G_ODR_SHIFT
CTRL2_G_ODR_833_HZ      = 0x07 << CTRL2_G_ODR_SHIFT
CTRL2_G_ODR_1_66_KHZ    = 0x08 << CTRL2_G_ODR_SHIFT

CTRL2_G_SCALE_SHIFT     = 0x02
CTRL2_G_SCALE_MASK      = 0x03 << CTRL2_G_SCALE_SHIFT
CTRL2_G_SCALE_250DPS    = 0x00 << CTRL2_G_SCALE_SHIFT
CTRL2_G_SCALE_500DPS    = 0x01 << CTRL2_G_SCALE_SHIFT
CTRL2_G_SCALE_1000DPS   = 0x02 << CTRL2_G_SCALE_SHIFT
CTRL2_G_SCALE_2000DPS   = 0x03 << CTRL2_G_SCALE_SHIFT

#CTRL3_C REGISTER (12h)
CTRL3_BOOT_SHIFT = 0X07
CTRL3_BOOT_MAKS  = 0X01 << CTRL3_BOOT_SHIFT
CTRL3_BOOT       = 0X01 << CTRL3_BOOT_SHIFT



# REG CTL9_XL Configurations
DEN_X_SHIFT     = 0x07
DEN_XYZ_MASK    = 0x03 << DEN_X_SHIFT
DEN_Y_SHIFT     = 0x06 
DEN_Z_SHIFT     = 0x05 

#REG D6D_SRC (1Dh)
D6D_SRC_DEN_DRDY_SHIFT  = 0X07 
D6D_SRC_DEN_DRDY_MASK   = 0X01 << D6D_SRC_DEN_DRDY_SHIFT
D6D_SRC_DEN_DRDY        = 0X01 << D6D_SRC_DEN_DRDY_SHIFT
D6D_SRC_POSITION_MASK   = 0X3F
D6D_SRC_XL              = 0X01 << 0
D6D_SRC_XH              = 0X01 << 1
D6D_SRC_YL              = 0X01 << 3
D6D_SRC_YH              = 0X01 << 4
D6D_SRC_ZL              = 0X01 << 5
D6D_SRC_ZH              = 0X01 << 6

#REG TAP_CFG2 (58h)
TAP_CFG2_INT_ENABLE_SHIFT                   = 0X07
TAP_CFG2_INT_ENABLE_MASK                    = 0X01 << TAP_CFG2_INT_ENABLE_SHIFT
TAP_CFG2_INT_ENABLED                        = 0X01 << TAP_CFG2_INT_ENABLE_SHIFT
TAP_CFG2_INT_DISABLED                       = 0X00 << TAP_CFG2_INT_ENABLE_SHIFT

TAP_CFG2_INACT_EN_SHIFT                     = 0X05
TAP_CFG2_INACT_EN_MASK                      = 0X03 << TAP_CFG2_INACT_EN_SHIFT
TAP_CFG2_INACT_EN_INT_ONLY                  = 0X00 << TAP_CFG2_INACT_EN_SHIFT
TAP_CFG2_INACT_EN_ACC_12_5_HZ               = 0X01 << TAP_CFG2_INACT_EN_SHIFT
TAP_CFG2_INACT_EN_ACC_12_5_HZ_GYRO_SLEEP    = 0X02 << TAP_CFG2_INACT_EN_SHIFT
TAP_CFG2_INACT_EN_ACC_12_5_HZ_GYRO_OFF      = 0X03 << TAP_CFG2_INACT_EN_SHIFT

#TAP_CFG2_THS_Y_MASK                         = 0X1F
#TAP_CFG2_THS_Y_SHIFT                        = 0X00
#TAP_CFG2_THS_Y_  #1LSB = FS_XL/(2^5)

#REG MD1_CFG (5Fh)
MD1_CFG_INT1_SLEEP_CHANGE_SHIFT  = 0X07
MD1_CFG_INT1_SLEEP_CHANGE_MAKS   = 0X01 << MD1_CFG_INT1_SLEEP_CHANGE_SHIFT

MD1_CFG_INT1_SINGLE_TAP_SHIFT    = 0X06
MD1_CFG_INT1_SINGLE_TAP_MASK     = 0X01 << MD1_CFG_INT1_SINGLE_TAP_SHIFT

MD1_CFG_INT1_WU_SHIFT           = 0X05
MD1_CFG_INT1_WU_MASK            = 0X01 << MD1_CFG_INT1_WU_SHIFT

MD1_CFG_INT1_FF_SHIFT           = 0X04
MD1_CFG_INT1_FF_MASK            = 0X01 << MD1_CFG_INT1_FF_SHIFT

MD1_CFG_INT1_DOUBLE_TAP_SHIFT  = 0X03
MD1_CFG_INT1_DOUBLE_TAP_MASK   = 0X01 << MD1_CFG_INT1_DOUBLE_TAP_SHIFT
 
MD1_CFG_INT1_6D_SHIFT           = 0X02
MD1_CFG_INT1_6D_MASK            = 0X01 << MD1_CFG_INT1_6D_SHIFT

MD1_CFG_INT1_EMB_FUNC_SHIFT     = 0X01
MD1_CFG_INT1_EMB_FUNC_MASK      = 0X01 << MD1_CFG_INT1_EMB_FUNC_SHIFT

MD1_CFG_INT1_SHUB_SHIFT         = 0X00
MD1_CFG_INT1_SHUB_MAKS          = 0X01 << MD1_CFG_INT1_SHUB_SHIFT

#REG ALL EVENT INTTERUPTS (1Ah)
ALL_INT_SRC_SLEEP_CHANGE    = 1 << 0X5
ALL_INT_SRC_D6D             = 1 << 0X4
ALL_INT_SRC_DOUBLE_TAP      = 1 << 0X3
ALL_INT_SRC_SINGLE_TAP      = 1 << 0X2
ALL_INT_SRC_WAKE_UP         = 1 << 0X1
ALL_INT_SRC_FF              = 1 << 0X0

#TAP_THS_6D (59h)
SIXD_THS_SHIFT = 0x05
SIXD_THS_MASK  = 0x03 << SIXD_THS_SHIFT
SIXD_THS_80D   = 0x00 << SIXD_THS_SHIFT
SIXD_THS_70D   = 0x01 << SIXD_THS_SHIFT
SIXD_THS_60D   = 0x02 << SIXD_THS_SHIFT
SIXD_THS_50D   = 0x03 << SIXD_THS_SHIFT

#REG WAKE_UP_THS (5Bh)
WAKE_UP_THS_SINGLE_DOUBLE_TAP_SHIFT = 0x07
WAKE_UP_THS_SINGLE_DOUBLE_TAP_MASK  = 0x01 << WAKE_UP_THS_SINGLE_DOUBLE_TAP_SHIFT
WAKE_UP_THS_SINGLE_ONLY_V           = 0X00 << WAKE_UP_THS_SINGLE_DOUBLE_TAP_SHIFT
WAKE_UP_THS_SINGLE_DOUBLE_V         = 0X01 << WAKE_UP_THS_SINGLE_DOUBLE_TAP_SHIFT

WAKE_UP_THS_USR_OFF_ON_WU_SHIFT     = 0X06
WAKE_UP_THS_USR_OFF_ON_WU_MAKS      = 0X01 << WAKE_UP_THS_USR_OFF_ON_WU_SHIFT

WAKE_UP_THS_WK_THS_SHIFT     = 0X00
WAKE_UP_THS_WK_THS_MASK      = 0X1F #WAKE UP WEIGHT DEPENDS ON WAKE_UP_DUR (5Ch)

#REG WAKE_UP_DUR (5Ch)
WAKE_UP_DUR_FF_DUR5_SHIFT = 0X07
WAKE_UP_DUR_FF_DUR5_MASK  = 0X01

WAKE_UP_DUR_WAKE_DUR_SHIFT  = 0X05
WAKE_UP_DUR_WAKE_DUR_MASK   = 0X03 << WAKE_UP_DUR_WAKE_DUR_SHIFT #wAKE UP DURRATION: 1LSB = 1 ODR TIME

WAKE_UP_DUR_SLEEP_DUR_SHIFT  = 0X00
WAKE_UP_DUR_SLEEP_DUR_MASK   = 0X07 << WAKE_UP_DUR_WAKE_DUR_SHIFT #SLEEP DURRATION: 1LSB = 512 ODR TIME



###Sensor hub###
#Slave X registers
SLVx_ADD_SHIFT      = 0X01
SLVx_ADD_MASK       = 0X7F << SLVx_ADD_SHIFT
SLVx_ADD_READ       = 0X01
SLVx_ADD_WRITE      = 0X00
SLVx_ADD_RW_MASK    = 0X01

SLVx_ODR_SHIFT      = 0X06
SLVx_ODR_MASK       = 0X03 << SLVx_ODR_SHIFT
SLVx_ODR_104HZ      = 0X00 
SLVx_ODR_52HZ       = 0X01 << SLVx_ODR_SHIFT
SLVx_ODR_26HZ       = 0X10 << SLVx_ODR_SHIFT
SLVx_ODR_12_5HZ     = 0X11 << SLVx_ODR_SHIFT

SLVx_FIFO_SHIFT     = 0X03
SLVx_FIFO_MASK      = 0X01 << SLVx_FIFO_SHIFT
SLVx_FIFO_ENABLE    = 0X01 << SLVx_FIFO_SHIFT
SLVx_FIFO_DISABLE   = 0X00 

SLVx_NUMOP_MASK     = 0X07

#Master Config (14h)

MASTER_CONFIG_RST_SHIFT  = 0X07
MASTER_CONFIG_RST_MASK   = 0X01 << MASTER_CONFIG_RST_SHIFT
MASTER_CONFIG_RESET      = 0X01 << MASTER_CONFIG_RST_SHIFT

MASTER_CONFIG_WRITE_ONCE_SHIFT  = 0X06
MASTER_CONFIG_WRITE_ONCE_MASK   = 0X01 << MASTER_CONFIG_WRITE_ONCE_SHIFT
MASTER_CONFIG_WRITE_ONCE        = 0X01 << MASTER_CONFIG_WRITE_ONCE_SHIFT

MASTER_CONFIG_START_CONFIG_SHIFT            = 0X05
MASTER_CONFIG_START_CONFIG_MASK             = 0X01 << MASTER_CONFIG_START_CONFIG_SHIFT
MASTER_CONFIG_START_CONFIG_TRIGGER_ACCEL    = 0X00 << MASTER_CONFIG_START_CONFIG_SHIFT
MASTER_CONFIG_START_CONFIG_TRIGGER_INT2     = 0X01 << MASTER_CONFIG_START_CONFIG_SHIFT

MASTER_CONFIG_PASS_THROUGH_SHIFT  = 0X04
MASTER_CONFIG_PASS_THROUGH_MASK   = 0X01 << MASTER_CONFIG_PASS_THROUGH_SHIFT
MASTER_CONFIG_PASS_THROUGH        = 0X01 << MASTER_CONFIG_PASS_THROUGH_SHIFT

MASTER_CONFIG_PU_EN_SHIFT  = 0X03
MASTER_CONFIG_PU_EN_MASK   = 0X01 << MASTER_CONFIG_PU_EN_SHIFT
MASTER_CONFIG_PU_EN        = 0X01 << MASTER_CONFIG_PU_EN_SHIFT

MASTER_CONFIG_MASTER_ON_SHIFT   = 0X02
MASTER_CONFIG_MASTER_ON_MASK    = 0X01 << MASTER_CONFIG_MASTER_ON_SHIFT
MASTER_CONFIG_MASTER_ON         = 0X01 << MASTER_CONFIG_MASTER_ON_SHIFT
MASTER_CONFIG_MASTER_OFF        = 0X00 << MASTER_CONFIG_MASTER_ON_SHIFT

MASTER_CONFIG_AUX_SENS_SHIFT   = 0X00
MASTER_CONFIG_AUX_SENS_MASK    = 0X03 << MASTER_CONFIG_AUX_SENS_SHIFT
MASTER_CONFIG_AUX_SENS_ONE     = 0X00 << MASTER_CONFIG_AUX_SENS_SHIFT
MASTER_CONFIG_AUX_SENS_TWO     = 0X01 << MASTER_CONFIG_AUX_SENS_SHIFT
MASTER_CONFIG_AUX_SENS_THREE   = 0X10 << MASTER_CONFIG_AUX_SENS_SHIFT
MASTER_CONFIG_AUX_SENS_FOUR    = 0X11 << MASTER_CONFIG_AUX_SENS_SHIFT

##SHUB status Master Register 

SHUB_STATUS_MASTER_WR_ONCE_DONE_SHIFT = 0X07
SHUB_STATUS_MASTER_WR_ONCE_DONE_MASK = 0X01 << SHUB_STATUS_MASTER_WR_ONCE_DONE_SHIFT
SHUB_STATUS_MASTER_SLV3_NACK_SHIFT = 0X06
SHUB_STATUS_MASTER_SLV3_NACK_MAKS = 0X01 << SHUB_STATUS_MASTER_SLV3_NACK_SHIFT
SHUB_STATUS_MASTER_SLV2_NACK_SHIFT = 0X05
SHUB_STATUS_MASTER_SLV2_NACK_MAKS = 0X01 << SHUB_STATUS_MASTER_SLV2_NACK_SHIFT
SHUB_STATUS_MASTER_SLV1_NACK_SHIFT = 0X04
SHUB_STATUS_MASTER_SLV1_NACK_MAKS = 0X01 << SHUB_STATUS_MASTER_SLV1_NACK_SHIFT
SHUB_STATUS_MASTER_SLV0_NACK_SHIFT = 0X03
SHUB_STATUS_MASTER_SLV0_NACK_MAKS = 0X01 << SHUB_STATUS_MASTER_SLV0_NACK_SHIFT
SHUB_END_OP_MAKS = 0X01
SHUB_END_OP_TRUE = 0X01


#####MAG Register Values######
#CTRL REG1
##EXCLUDED TEMP 
MAG_CTRL1_OM_SHIFT      =0X05
MAG_CTRL1_OM_MASK       =0X03 << MAG_CTRL1_OM_SHIFT
MAG_CTRL1_ODR_80HZ         =0X00
MAG_CTRL1_OM_MP         =0X01 << MAG_CTRL1_OM_SHIFT
MAG_CTRL1_OM_HP         =0X02 << MAG_CTRL1_OM_SHIFT
MAG_CTRL1_OM_UHP        =0X03 << MAG_CTRL1_OM_SHIFT

MAG_CTRL1_ODR_SHIFT     =0X02 
MAG_CTRL1_ODR_MAKS      =0X07 << MAG_CTRL1_ODR_SHIFT
MAG_CTRL1_ODR_MAKS      =0X07 << MAG_CTRL1_ODR_SHIFT
MAG_CTRL1_ODR_0_626HZ   =0X00 << MAG_CTRL1_ODR_SHIFT
MAG_CTRL1_ODR_1_25HZ    =0X01 << MAG_CTRL1_ODR_SHIFT
MAG_CTRL1_ODR_2_5HZ     =0X02 << MAG_CTRL1_ODR_SHIFT
MAG_CTRL1_ODR_5HZ       =0X03 << MAG_CTRL1_ODR_SHIFT
MAG_CTRL1_ODR_10HZ      =0X04 << MAG_CTRL1_ODR_SHIFT
MAG_CTRL1_ODR_20HZ      =0X05 << MAG_CTRL1_ODR_SHIFT
MAG_CTRL1_ODR_40HZ      =0X06 << MAG_CTRL1_ODR_SHIFT
MAG_CTRL1_ODR_80HZ      =0X07 << MAG_CTRL1_ODR_SHIFT

##EXCLUDE FAST ODR (ADD FOR RATES > 80HZ)
##EXCLUDE SELF TEST

#CTRL REG2 
MAG_CTRL2_FS_SHIFT      =0X05
MAG_CTRL2_FS_MASK       =0X03
MAG_CTRL2_FS_4G         =0X00 << MAG_CTRL2_FS_SHIFT
MAG_CTRL2_FS_8G         =0X01 << MAG_CTRL2_FS_SHIFT
MAG_CTRL2_FS_12G        =0X02 << MAG_CTRL2_FS_SHIFT
MAG_CTRL2_FS_16G        =0X03 << MAG_CTRL2_FS_SHIFT

MAG_CTRL2_REBOOT_SHIFT  =0X03
MAG_CTRL2_REBOOT_MAKS   =0X01 << MAG_CTRL2_REBOOT_SHIFT
MAG_CTRL2_REBOOT        =0X01 << MAG_CTRL2_REBOOT_SHIFT

MAG_CTRL2_SOFT_RST_SHIFT  =0X02
MAG_CTRL2_SOFT_RST_MAKS   =0X01 << MAG_CTRL2_SOFT_RST_SHIFT
MAG_CTRL2_SOFT_RST        =0X01 << MAG_CTRL2_SOFT_RST_SHIFT

## CTRL REG 3
MAG_CTRL3_MD_MAKS           = 0X03
MAG_CTRL3_MD_CONTINUOUS     = 0X00
MAG_CTRL3_MD_SINGLE         = 0X01
MAG_CTRL3_MD_POWER_DOWN     = 0X03


# Linear acceleration sensitivity
LA_So = {CTRL1_XL_SCALE_2G: 0.061, CTRL1_XL_SCALE_4G: 0.122,
         CTRL1_XL_SCALE_8G: 0.244, CTRL1_XL_SCALE_16G: 0.488}

# Angular rate sensitivity
G_So = {CTRL2_G_SCALE_250DPS: 8.75, CTRL2_G_SCALE_500DPS: 17.50,
        CTRL2_G_SCALE_1000DPS: 35, CTRL2_G_SCALE_2000DPS: 70}

M_So = {MAG_CTRL2_FS_4G: 6842, MAG_CTRL2_FS_8G: 3421,
        MAG_CTRL2_FS_12G: 2281, MAG_CTRL2_FS_16G: 1711}


class LSM6DSOX:

    event_callbacks = [None, None, None, None, None]


    FUNC_CFG_ACCESS_REG = 0x01
    PIN_CTRL_REG = 0x02
    SENSOR_SYNC_TIME_FRAME_L_REG = 0x4
    SENSOR_SYNC_TIME_FRAME_H_REG = 0x05
    SENSOR_SYNC_RESOLUTION_RATIO_REG = 0x06
    FIFO_CTRL1_REG = 0x07
    FIFO_CTRL2_REG = 0x08
    FIFO_CTRL3_REG = 0x09
    FIFO_CTRL4_REG = 0x0A
    COUNTER_BDR_REG1_REG = 0x0B
    COUNTER_BDR_REG2_REG = 0x0C
    INT1_CTRL_REG = 0x0D
    INT2_CTRL_REG = 0x0E
    WHO_AM_I_REG = 0x0F
    CTRL1_XL_REG = 0x10
    CTRL2_G_REG = 0x11
    CTRL3_C_REG = 0x12
    CTRL4_C_REG = 0x13
    CTRL5_C_REG = 0x14
    CTRL6_C_REG = 0x15
    CTRL7_G_REG = 0x16
    CTRL8_XL_REG = 0x17
    CTRL9_XL_REG = 0x18
    CTRL10_C_REG = 0x19
    ALL_INT_SRC_REG = 0x1A
    WAKE_UP_SRC_REG = 0x1B
    TAP_SRC_REG = 0x1C
    D6D_SRC_REG = 0x1D
    STATUS_REG_REG = 0x1E
    OUT_TEMP_L_REG = 0x20
    OUT_TEMP_H_REG = 0x21
    OUTX_L_G_REG = 0x22
    OUTX_H_G_REG = 0x23
    OUTY_L_G_REG = 0x24
    OUTY_H_G_REG = 0x25
    OUTZ_L_G_REG = 0x26
    OUTZ_H_G_REG = 0x27
    OUTX_L_XL_REG = 0x28
    OUTX_H_XL_REG = 0x29
    OUTY_L_XL_REG = 0x2A
    OUTY_H_XL_REG = 0x2B
    OUTZ_L_XL_REG = 0x2C
    OUTZ_H_XL_REG = 0x2D
    EMB_FUNC_STATUS_MAINPAGE_REG = 0x35
    FSM_STATUS_A_MAINPAGE_REG = 0x036
    FSM_STATUS_B_MAINPAGE_REG = 0x037
    MLC_STATUS_MAINPAGE_REG = 0x38
    STATUS_MASTER_MAINPAGE_REG = 0x39
    FIFO_STATUS1_REG = 0x3A
    FIFO_STATUS2_REG = 0x3B
    TIMESTAMP0_REG = 0x40
    TIMESTAMP1_REG = 0x41
    TIMESTAMP2_REG = 0x42
    TIMESTAMP3_REG = 0x43
    #SKIPPED OSI REGISTERS 0x49 - 0x55#
    TAP_CFG0_REG = 0x56
    TAP_CFG1_REG = 0x57
    TAP_CFG2_REG = 0x58
    TAP_THS_6D_REG = 0x59
    INT_DUR2_REG = 0x5A
    WAKE_UP_THS_REG = 0x5B
    WAKE_UP_DUR_REG = 0x5C
    FREE_FALL_REG = 0x5D
    MD1_CFG_REG = 0x5E
    MD2_CFG_REG = 0x5F
    S4S_ST_CMD_CODE_REG = 0X60
    S4S_DT_REG_REG = 0x61

    ## SENSOR HUB
    SHUB_1  = 0X02
    SHUB_2  = 0X03
    SHUB_3  = 0X04
    SHUB_4  = 0X05
    SHUB_5  = 0X06
    SHUB_6  = 0X07
    SHUB_7  = 0X08
    SHUB_8  = 0X09
    SHUB_9  = 0X0A
    SHUB_10 = 0X0B
    SHUB_11 = 0X0C
    SHUB_12 = 0X0D
    SHUB_13 = 0X0E
    SHUB_14 = 0X0F
    SHUB_15 = 0X10
    SHUB_16 = 0X11
    SHUB_17 = 0X12
    SHUB_18 = 0X13

    SHUB_MASTER_CONFIG = 0X14

    SHUB_SLV0_ADD      = 0X15
    SHUB_SLV0_SUBADD   = 0X16
    SHUB_SLV0_CONFIG   = 0X17
    SHUB_SLV1_ADD      = 0X18
    SHUB_SLV1_SUBADD   = 0X19
    SHUB_SLV1_CONFIG   = 0X1A
    SHUB_SLV2_ADD      = 0X1B
    SHUB_SLV2_SUBADD   = 0X1C
    SHUB_SLV2_CONFIG   = 0X1D
    SHUB_SLV3_ADD      = 0X1E
    SHUB_SLV3_SUBADD   = 0X1F
    SHUB_SLV3_CONFIG   = 0X20

    SHUB_DATA_WRITE_SLV0 = 0X21
    SHUB_STATUS_MASTER   = 0X22

    ##MAG REGISTERS##
    MAG_WHO_AM_I  = 0x0F
    MAG_CTRL_REG1 = 0X20
    MAG_CTRL_REG2 = 0X21
    MAG_CTRL_REG3 = 0X22
    MAG_CTRL_REG4 = 0X23
    MAG_CTRL_REG5 = 0X24
    MAG_STATUS_REG = 0X27
    MAG_OUT_X_L = 0X28
    MAG_OUT_X_H = 0X29
    MAG_OUT_Y_L = 0X2A
    MAG_OUT_Y_H = 0X2B
    MAG_OUT_Z_L = 0X2C
    MAG_OUT_Z_H = 0X2D


    def __init__(self, acc_odr=CTRL1_XL_ODR_POWER_DOWN, gyro_odr=CTRL2_G_ODR_POWER_DOWN,
                 acc_scale=CTRL1_XL_SCALE_2G, gyro_scale=CTRL2_G_SCALE_250DPS, 
                 mag_scale=MAG_CTRL2_FS_4G, mag_odr = MAG_CTRL1_ODR_80HZ, mag_enable = False,
                 debug_level = 'DEBUG' ):

        #Logger
        self.logger = logging.getLogger('lsm6dsox_imu')
        self.logger.addHandler(logging.StreamHandler())
        level = logging.getLevelName(debug_level)
        self.logger.setLevel(level)

        self.__name__ = "LSM6DSOX"
        self.LSM6DSOX_ADDRESS = LSM6DSOX_ADDRESS

        #Sensor Configuration values
        self.__ACC_SCALE = acc_scale
        self.__ACC_ODR = acc_odr

        self.__GYRO_SCALE = gyro_scale
        self.__GYRO_ODR = gyro_odr

        self.__MAG_SCALE =  mag_scale
        self.__MAG_ODR   =  mag_odr 
        self.mag_enabled = mag_enable

        #Event Callbacks for INT1 
        self.on_D6D_change      = None
        self.on_sleep_change    = None
        self.on_double_tap      = None #TODO
        self.on_single_tap      = None #TODO
        self.on_wake_up         = None #TODO
        self.on_sensor_data     = None

        # State Variables
        self.__is_shub_reg_access_en    = False 
        self.__is_basic_interrupts      = False
        self.__is_initialized = self.__initialize()


    def __initialize(self):
        self.__shub_register_access(FUN_SHUB_DISABLE) # ensure sensor hub access is turned off
        self.__i2c_write_reg(self.CTRL3_C_REG, CTRL3_BOOT) #Preform soft reset 
        self.disable_data_ready_int()
        time.sleep(.1)

        self.__init_accelerometer()
        self.__init_gyroscope()
        
        if self.mag_enabled:
            self.__init_magnetometer()
        
        self.__route_int1_functions(0xff, 0x00) #clear all interrupt sources
        self.__enable_basic_interrupts()
        self.__initialize_gpio_interrupts()
   
        return True
    
    # enables the data ready 
    def enable_data_ready_int(self, callback, accel, gyro):
        self.on_sensor_data = callback
        data = accel | (gyro << 1) #(pg 55)
        self.__i2c_modifyReg(self.INT2_CTRL_REG, 0x03, data)
        self.__i2c_modifyReg(self.COUNTER_BDR_REG1_REG, 1 << 7, 1 << 7)
        #self.logger.debug(self.__i2c_read_reg(self.INT2_CTRL_REG))

        #self.__i2c_modifyReg(self.CTRL4_C_REG, 0x08, 0x08)\

        # Disables the data ready on INT2
    def disable_data_ready_int(self):
        self.on_sensor_data = None
        
        self.__i2c_modifyReg(self.INT2_CTRL_REG, 0x03, 0x00)
        self.__i2c_modifyReg(self.COUNTER_BDR_REG1_REG, 1 << 7, 0 << 7)
        #self.logger.debug(self.__i2c_read_reg(self.INT2_CTRL_REG))

        #self.__i2c_modifyReg(self.CTRL4_C_REG, 0x08, 0x08)

    def __deinitialize(self):
        print("DEL IMU")
        if self.__is_initialized:  
            self.disable_data_ready_int()
            self.__powerdown_accelerometer()
            self.__powerdown_gyroscope()
            self.__shub_enable_master_i2c(MASTER_CONFIG_MASTER_OFF)


    def __del__(self):
        self.__deinitialize()


    def __i2c_read_reg(self, reg, b=1):
        try:
            if b == 1:
                return bus.read_byte_data(self.LSM6DSOX_ADDRESS, reg)
            else:
                return bus.read_i2c_block_data(self.LSM6DSOX_ADDRESS, reg, b)
        except Exception as e:
            self.logger.warning('WARNING: Read Reg exception %s' % e)


    def read_reg(self,reg,b=1):
        return self.__i2c_read_reg(reg,b)


    def __i2c_write_reg(self, reg, data, b=1):
        try:
            if b == 1:
                bus.write_byte_data(self.LSM6DSOX_ADDRESS, reg, data)
            else:
                return bus.write_i2c_block_data(self.LSM6DSOX_ADDRESS, reg, data)
        except Exception as e:
            self.logger.warning('WARNING: Write reg exception %s' % e)


    def __i2c_modifyReg(self, reg, mask, data):
        try:
         return self.__i2c_write_reg(reg, (self.__i2c_read_reg(reg) & (~mask)) | data)
        except Exception as e:
            self.logger.warning('WARNING: Modify Reg exception %s' % e)


    def getWhoAmI(self):
        return self.__i2c_read_reg(self.WHO_AM_I_REG)


    def __init_accelerometer(self):

        # SetAccelerometer Output Data Rate & Full Scale
        data = (self.__ACC_ODR) | (self.__ACC_SCALE)
        mask = (CTRL1_XL_ODR_MASK) | (CTRL1_XL_SCALE_MASK)
        self.__i2c_modifyReg(self.CTRL1_XL_REG, mask, data)


    def __init_gyroscope(self):

        data = (self.__GYRO_ODR) | (self.__GYRO_SCALE)
        mask = (CTRL2_G_ODR_MASK) | (CTRL2_G_ODR_MASK)
        self.__i2c_modifyReg(self.CTRL2_G_REG, mask, data)


    def __powerdown_accelerometer(self):
        # Power-down accelerometer
        self.__i2c_modifyReg(self.CTRL1_XL_REG, CTRL1_XL_ODR_MASK , CTRL1_XL_ODR_POWER_DOWN)


    def __powerdown_gyroscope(self):
        # Power down Gyroscope
        self.__i2c_modifyReg(self.CTRL2_G_REG, CTRL2_G_ODR_MASK <<
                         CTRL2_G_ODR_SHIFT,  CTRL2_G_ODR_POWER_DOWN)


    def get_status(self):
        return self.__i2c_read_reg(self.STATUS_REG_REG)


    def get_mag_status(self):
        self.__shub_register_access(FUN_SHUB_ENABLE)
        status = self.__i2c_read_reg(self.SHUB_7)
        self.__shub_register_access(FUN_SHUB_DISABLE)
        return status


    def getAccData(self, raw=False):
        acc_x = self.__getAccDataX(raw)
        acc_y = self.__getAccDataY(raw)
        acc_z = self.__getAccDataZ(raw)
        return [acc_x, acc_y, acc_z]


    def __getAccDataX(self, raw):
        acc_l = self.__i2c_read_reg(self.OUTX_L_XL_REG)
        acc_h = self.__i2c_read_reg(self.OUTX_H_XL_REG)
        combined = (acc_h << 8) | acc_l

        if raw:
            return combined
        return c_int16(combined).value*LA_So[self.__ACC_SCALE]


    def __getAccDataY(self, raw):
        acc_l = self.__i2c_read_reg(self.OUTY_L_XL_REG)
        acc_h = self.__i2c_read_reg(self.OUTY_H_XL_REG)
        combined = (acc_h << 8) | acc_l

        if raw:
            return combined
        return c_int16(combined).value*LA_So[self.__ACC_SCALE]


    def __getAccDataZ(self, raw):
        acc_l = self.__i2c_read_reg(self.OUTZ_L_XL_REG)
        acc_h = self.__i2c_read_reg(self.OUTZ_H_XL_REG)
        combined = (acc_h << 8) | acc_l
        
        if raw:
            return combined
        
        return c_int16(combined).value*LA_So[self.__ACC_SCALE]


    def __getGyroDataX(self, raw):
        gyro_l = self.__i2c_read_reg(self.OUTX_L_G_REG)
        gyro_h = self.__i2c_read_reg(self.OUTX_H_G_REG)
        combined = gyro_h << 8 | gyro_l

        if raw:
            return combined
        return c_int16(combined).value*G_So[self.__GYRO_SCALE]


    def __getGyroDataY(self, raw):
        gyro_l = self.__i2c_read_reg(self.OUTY_L_G_REG)
        gyro_h = self.__i2c_read_reg(self.OUTY_H_G_REG)
        combined = gyro_h << 8 | gyro_l

        if raw:
            return combined
        return c_int16(combined).value*G_So[self.__GYRO_SCALE]


    def __getGyroDataZ(self, raw):
        gyro_l = self.__i2c_read_reg(self.OUTZ_L_G_REG)
        gyro_h = self.__i2c_read_reg(self.OUTZ_H_G_REG)
        combined = gyro_h << 8 | gyro_l

        if raw:
            return combined
        return c_int16(combined).value*G_So[self.__GYRO_SCALE]


    def getGyroData(self, raw=False):
        gyro_x = self.__getGyroDataX(raw)
        gyro_y = self.__getGyroDataY(raw)
        gyro_z = self.__getGyroDataZ(raw)

        return [gyro_x, gyro_y, gyro_z]


    def getAccGyroData(self):
        acc_data = self.getAccData()
        gyro_data = self.getGyroData()
        return acc_data + gyro_data


    def __get_mag_x(self, raw):
        mag_l = self.__i2c_read_reg(self.SHUB_2)
        mag_h = self.__i2c_read_reg(self.SHUB_3)
        combined = mag_h << 8 | mag_l

        if raw:
            return combined
        return c_int16(combined).value / M_So[self.__MAG_SCALE]


    def __get_mag_y(self, raw):
        mag_l = self.__i2c_read_reg(self.SHUB_4)
        mag_h = self.__i2c_read_reg(self.SHUB_5)
        combined = mag_h << 8 | mag_l

        if raw:
            return combined
        return c_int16(combined).value / M_So[self.__MAG_SCALE]


    def __get_mag_z(self, raw):
        mag_l = self.__i2c_read_reg(self.SHUB_6)
        mag_h = self.__i2c_read_reg(self.SHUB_7)
        combined = mag_h << 8 | mag_l

        if raw:
            return combined
        return c_int16(combined).value / M_So[self.__MAG_SCALE]


    def get_mag_data(self, raw=False):

        if self.mag_enabled:
            self.__shub_register_access(FUN_SHUB_ENABLE)
            mag_x = self.__get_mag_x(raw)
            mag_y = self.__get_mag_y(raw)
            mag_z = self.__get_mag_z(raw)
            self.__shub_register_access(FUN_SHUB_DISABLE)

            return [mag_x, mag_y, mag_z]
        else:
            return [0, 0, 0]
         

    # Enables d6d oriantation detection on Interrupt line 1 GPIO4
    # @param callback function callback for interrupt 
    # @param threshold angle threshold 50 to 80 degress [SIXD_THS_XX]
    def enable_d6d_event(self, callback, threshold = SIXD_THS_70D):  
        self.__route_int1_functions(MD1_CFG_INT1_6D_MASK, 1 << MD1_CFG_INT1_6D_SHIFT) 
        self.__i2c_modifyReg(self.TAP_THS_6D_REG, SIXD_THS_MASK, threshold)
        self.on_D6D_change = callback

    # Disables 6D event interrupts on interrupt line 1 GPIO4
    def disable_d6d_event(self):
        self.__route_int1_functions(MD1_CFG_INT1_6D_MASK, 0 << MD1_CFG_INT1_6D_SHIFT) 
        self.on_D6D_change = None
 
    #Returns the curent orientation 
    def get_d6d_source(self):
        return (self.__i2c_read_reg(self.D6D_SRC_REG) & D6D_SRC_POSITION_MASK)


    # Enables the sleep change event and attaches the event to interrupt line 1 (GPIO4)
    # @param callback function callback for intrrupt
    # @param wake_ths Threshold for wakeup: 1 LSB weight depends on WAKE_THS_W in WAKE_UP_DUR (5Ch). 1 LSB = FS_XL / (26)
    # @param wake_dur Wake up duration event. 1LSB = 1 ODR time 
    # @param sleep_dur Duration to go in sleep mode. Default value: 0000 (this corresponds to 16 ODR) 1 LSB = 512 ODR
    def enable_sleep_change_event(self, callback, wake_ths = 0x02, wake_dur = 0x01, sleep_dur = 0x01):  
        
        #set wakeup threshold 
        self.__i2c_modifyReg(self.WAKE_UP_THS_REG, WAKE_UP_THS_WK_THS_MASK, wake_ths << WAKE_UP_THS_WK_THS_SHIFT) #(pg 85)
        
        #Set wakeup and sleep durations 
        self.__i2c_modifyReg(self.WAKE_UP_DUR_REG, WAKE_UP_DUR_WAKE_DUR_MASK | WAKE_UP_DUR_SLEEP_DUR_MASK,\
                        (wake_dur << WAKE_UP_DUR_WAKE_DUR_SHIFT) | (sleep_dur << WAKE_UP_DUR_SLEEP_DUR_SHIFT) ) #(pg 86)
        
        #Enable sleep change interrupt on INT1
        self.__route_int1_functions(MD1_CFG_INT1_SLEEP_CHANGE_MAKS, 1 << MD1_CFG_INT1_SLEEP_CHANGE_SHIFT)  
        
        #Set callback for sleep event change
        self.on_sleep_change = callback

    # Disables the sleep event
    def disable_sleep_change_event(self, callback, wake_ths = 0x02, wake_dur = 0x01, sleep_dur = 0x01):  
               
        #Removes sleep change interrupt on INT1
        self.__route_int1_functions(MD1_CFG_INT1_SLEEP_CHANGE_MAKS, 0 << MD1_CFG_INT1_SLEEP_CHANGE_SHIFT)  
        
        #Clear callback
        self.on_sleep_change = None
 
    # Read wakeup source change
    def get_wakeup_source(self):
        return (self.__i2c_read_reg(self.WAKE_UP_SRC_REG))

    # Read all interrupt sorce (1Ah)
    def __get_event_interrupt_src(self):
        return self.__i2c_read_reg(self.ALL_INT_SRC_REG)


    # Enables interrupt and inactivity functions, and tap recognition functions 
    # @param inact_en defines the ODR behavior when in inactive mode (pg 83)
    # sets interrupt enable bit in TAP_CFG2 (58h) 
    def __enable_basic_interrupts(self, inact_en = TAP_CFG2_INACT_EN_INT_ONLY):  
        data = (TAP_CFG2_INT_ENABLED) | inact_en
        mask = (TAP_CFG2_INT_ENABLE_MASK) | (TAP_CFG2_INACT_EN_MASK)
        self.__i2c_modifyReg(self.TAP_CFG2_REG, mask, data)
        self.__is_basic_interrupts = True

    # Registers events to interrupt line 1 
    def __route_int1_functions(self, mask, data):
        return self.__i2c_modifyReg(self.MD1_CFG_REG, mask, data)

    # GPIO config for INT1 (GPIO4) and INT2 (GPIO17)
    def __initialize_gpio_interrupts(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(INTERRUPT_1_PIN, GPIO.IN)
        GPIO.add_event_detect(INTERRUPT_1_PIN, GPIO.RISING, callback=self.__interrupt_1_handler)
        
        GPIO.setup(INTERRUPT_2_PIN, GPIO.IN)
        GPIO.add_event_detect(INTERRUPT_2_PIN, GPIO.RISING, callback=self.__interrupt_2_handler)
    
        #Handle Events
    
    # Interrupt 1 handler
    # Reads the source of the interrupt and calls the application callback 
    def __interrupt_1_handler(self, channel):
        
        src = self.__get_event_interrupt_src()

        if src & ALL_INT_SRC_SLEEP_CHANGE:
            if self.on_sleep_change != None:
                self.on_sleep_change(self.get_wakeup_source())
        
        if src & ALL_INT_SRC_D6D:
            if self.on_D6D_change != None:
                self.on_D6D_change(self.get_d6d_source())
        
        if src & ALL_INT_SRC_DOUBLE_TAP:
            pass #TODO impliment double tap

        if src & ALL_INT_SRC_SINGLE_TAP:
            pass #TODO impliment single tap
        
        # if src & ALL_INT_SRC_WAKE_UP:
        #     pass

        if src & ALL_INT_SRC_FF:
            pass
            #print("free fall")
        
    
    
    def __interrupt_2_handler(self, channel):
        if self.on_sensor_data != None: 
            self.on_sensor_data()


####################### MAGNETOMETER SENSOR HUB #######################

    # Turn on sensor hub to write to sensor hub registers
    # @param fun_shub_val FUN_SHUB_DISABLE OR FUN_SHUB_ENABLE
    def __shub_register_access(self, fun_shub_val):  
        #tun on Sensor Hub Access 
        self.logger.debug(f"[Debug] Sensor hub register access {fun_shub_val}")  
        self.__i2c_modifyReg(self.FUNC_CFG_ACCESS_REG, FUN_SHUB_REG_ACCESS_MASK, fun_shub_val)
        self.__is_shub_reg_access_en = fun_shub_val


    # Turns on and off the sensor hub master I2C bus
    # @param Val MASTER_CONFIG_MASTER_ON or MASTER_CONFIG_MASTER_OFF
    def __shub_enable_master_i2c(self, val):
        if not self.__is_shub_reg_access_en:
            raise Exception(f"Sensor hub not enable")
        self.__i2c_modifyReg(self.SHUB_MASTER_CONFIG, MASTER_CONFIG_MASTER_ON_MASK, val)
        self.logger.debug(f"[Shub en i2c] {self.__i2c_read_reg(self.SHUB_MASTER_CONFIG)}")

    # Returns sensor hub status 
    def __shub_status(self): 
        if not self.__is_shub_reg_access_en:
            raise Exception(f"Sensor hub not enable")
        status = self.__i2c_read_reg(self.SHUB_STATUS_MASTER)
        return status


    # Sets up a slave device writing to the address, sub address and control registers 
    # @param slvx_base Slave base address register [0-3] ex. SLV0_ADD = 0x15
    # @param slvx_add  Sensor Address, ie magnetometer i2c address
    # @param r_w read or write register. NOTE: only slave 0 can write to a register.        
    # @param slvx_subadd slave address to read / write to.
    # @param slvx_odr Rate at which the master communicates. NOTE: only available on slave 0
    # @param slvx_fifo_en  TODO FIFO not enabled yet. 
    # @param slvx_numop Number of read operations on Sensor X
    def __shub_configure_slave_sensor(self, slvx_base, slvx_add, r_w, slvx_subadd, slvx_odr, slvx_fifo_en, slvx_numop):
        
        address = (slvx_add << 1) | r_w
        
        
        config =(slvx_fifo_en << SLVx_FIFO_SHIFT) | (slvx_numop) #TODO BUG HERE, only slave 0 uses this config

        if slvx_base == self.SHUB_SLV0_ADD:
            config = config | (slvx_odr << SLVx_ODR_SHIFT)  #Only slv0 has a ODR 

        if not self.__is_shub_reg_access_en:
            raise Exception(f"Sensor hub not enable")
            
        self.__i2c_write_reg(slvx_base, address)          #slave address register
        self.__i2c_write_reg(slvx_base + 1, slvx_subadd)  #slave sub reg
        self.__i2c_write_reg(slvx_base + 2 , config)      #slave config register  
        return SUCCESS


    # Writes to the Magnetometer via the LSM6DSOX sensor hub registers. 
    # See LSM6DSOX datasheet section 17
    # @param reg is the Magnetometer register being written to
    # @param val is the Magnetometer register value to write 
    # @param write_once is a bool to wrtie to the register continuosly or once
    # returns SUCCESS = 0 or ERROR = -1
    def __mag_write_reg(self, reg, val, write_once = True):
        ## Write to sensor hub 0
        TIMEOUT = 10
        if not self.__is_shub_reg_access_en:
            raise Exception(f"Sensor hub not enable")
        
        self.logger.debug(f"[Mag ctr Reg][REG VAL ONCE] {reg} {val} {write_once}")
        
        master_i2c = self.__i2c_read_reg(self.SHUB_MASTER_CONFIG) & MASTER_CONFIG_MASTER_ON_MASK

        if write_once:
            self.__shub_enable_master_i2c(MASTER_CONFIG_MASTER_OFF)

        #Set up contol
        self.__shub_configure_slave_sensor(self.SHUB_SLV0_ADD, LIS3MDL_ADDRESS, SLVx_ADD_WRITE, reg, SLVx_ODR_52HZ, False, 0)
        
        self.__i2c_write_reg(self.SHUB_DATA_WRITE_SLV0, val)
        self.__shub_enable_master_i2c(MASTER_CONFIG_MASTER_ON) #transmit 

        timeout = 0
        status = self.__shub_status() & SHUB_STATUS_MASTER_WR_ONCE_DONE_MASK
        while not status and write_once and timeout < TIMEOUT :
            self.logger.debug(f"[Mag ctr Reg] Status: {status}  Timeout {timeout} ")
            status = self.__shub_status() & SHUB_STATUS_MASTER_WR_ONCE_DONE_MASK
            timeout += 1
            time.sleep(.1)
         
        self.__shub_enable_master_i2c(master_i2c) #Return I2C Master to the original state before call
        
        if timeout >= TIMEOUT: 
            self.__shub_register_access(FUN_SHUB_DISABLE)
            self.__shub_enable_master_i2c(MASTER_CONFIG_MASTER_OFF)
            self.logger.warning(f"WARNING: Magnetometer failed to initialize {reg}")
            self.mag_enabled = False
            return ERROR
        else: 
            return SUCCESS


    # Sets up the Magnetometer based on the Class init values
    # Writes to the mag control registers
    # Sets up the Sensor hub Slave 0 to read X Y Z values on 52hz interval
    def __init_magnetometer(self):
        
        self.logger.debug("[Magnetometer] Init Start")

        if not self.__is_shub_reg_access_en:
            self.__shub_register_access(FUN_SHUB_ENABLE)

        ##Reset sensor hub
        self.__i2c_write_reg(self.SHUB_MASTER_CONFIG, MASTER_CONFIG_RESET )
        
        #Write once mode and pullup enabled =
        self.__i2c_write_reg(self.SHUB_MASTER_CONFIG,  MASTER_CONFIG_PU_EN | MASTER_CONFIG_AUX_SENS_TWO | MASTER_CONFIG_WRITE_ONCE)
        
        ##Write the control registers. If fail, stop init and disable the accelerometer
        if self.__mag_write_reg(self.MAG_CTRL_REG1, self.__MAG_ODR | MAG_CTRL1_OM_MP): return
        if self.__mag_write_reg(self.MAG_CTRL_REG2, self.__MAG_SCALE): return
        if self.__mag_write_reg(self.MAG_CTRL_REG4, 0x3 << 0x2): return #Z axis mode
        if self.__mag_write_reg(self.MAG_CTRL_REG5, 0x01): return #Data blocking mode
        
        #turn off write once to start single conversion conversion that is needed at low data rates
        self.__i2c_modifyReg(self.SHUB_MASTER_CONFIG, MASTER_CONFIG_WRITE_ONCE_MASK, 0x00)
        if self.__mag_write_reg(self.MAG_CTRL_REG3, MAG_CTRL3_MD_SINGLE, False): return
 
        self.__shub_enable_master_i2c(MASTER_CONFIG_MASTER_OFF)

        #Set up hub slave 1 for X Y Z reads (6 addreses)
        self.__shub_configure_slave_sensor(self.SHUB_SLV1_ADD, LIS3MDL_ADDRESS, SLVx_ADD_READ, self.MAG_STATUS_REG, SLVx_ODR_52HZ, False, 0x07)
    
        #Turn On Sensor hub I2C buss 
        self.__shub_enable_master_i2c(MASTER_CONFIG_MASTER_ON)      

        self.__shub_register_access(FUN_SHUB_DISABLE)
        self.logger.debug("[Magnetometer] Init Complete")
