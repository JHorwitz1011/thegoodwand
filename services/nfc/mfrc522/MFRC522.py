#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#    Copyright 2014,2018 Mario Gomez <mario.gomez@teubi.co>
#
#    This file is part of MFRC522-Python
#    MFRC522-Python is a simple Python implementation for
#    the MFRC522 NFC Card Reader for the Raspberry Pi.
#
#    MFRC522-Python is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    MFRC522-Python is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with MFRC522-Python.  If not, see <http://www.gnu.org/licenses/>.
#    https://sweet.ua.pt/andre.zuquete/Aulas/IRFID/11-12/docs/IRFID_avz_2.pdf
#    
#    https://stackoverflow.com/questions/45545493/distinguish-different-types-of-mifare-ultralight
#
import RPi.GPIO as GPIO
import spidev
import signal
import time
import logging

class MFRC522:
    MAX_LEN = 16

    #commands for command reg bit 0-3 Pg. 70 of datasheet
    PCD_IDLE = 0x00
    PCD_AUTHENT = 0x0E
    PCD_RECEIVE = 0x08
    PCD_TRANSMIT = 0x04
    PCD_TRANSCEIVE = 0x0C #transmits data from FIFO buffer to antenna and automatically activates the receiver after transmission
    PCD_RESETPHASE = 0x0F
    PCD_CALCCRC = 0x03

    #command set for NFC tags 
    PICC_REQIDL = 0x26
    PICC_REQALL = 0x52
    PICC_ANTICOLL = 0x93
    PICC_SElECTTAG = 0x93
    #PICC_AUTHENT1A = 0x60
    #PICC_AUTHENT1B = 0x61
    PICC_GETVERSION= 0x60
    PICC_READ = 0x30
    PICC_WRITE = 0xA0
    PICC_DECREMENT = 0xC0
    PICC_INCREMENT = 0xC1
    PICC_RESTORE = 0xC2
    PICC_TRANSFER = 0xB0
    PICC_HALT = 0x50

    MI_OK = 0
    MI_NOTAGERR = 1
    MI_ERR = 2

    #MFRC522 registers
    Reserved00 = 0x00
    CommandReg = 0x01
    CommIEnReg = 0x02
    DivlEnReg = 0x03
    CommIrqReg = 0x04
    DivIrqReg = 0x05
    ErrorReg = 0x06
    Status1Reg = 0x07
    Status2Reg = 0x08
    FIFODataReg = 0x09
    FIFOLevelReg = 0x0A
    WaterLevelReg = 0x0B
    ControlReg = 0x0C
    BitFramingReg = 0x0D
    CollReg = 0x0E
    Reserved01 = 0x0F

    Reserved10 = 0x10
    ModeReg = 0x11
    TxModeReg = 0x12
    RxModeReg = 0x13
    TxControlReg = 0x14
    TxAutoReg = 0x15
    TxSelReg = 0x16
    RxSelReg = 0x17
    RxThresholdReg = 0x18
    DemodReg = 0x19
    Reserved11 = 0x1A
    Reserved12 = 0x1B
    MifareReg = 0x1C
    Reserved13 = 0x1D
    Reserved14 = 0x1E
    SerialSpeedReg = 0x1F

    Reserved20 = 0x20
    CRCResultRegM = 0x21
    CRCResultRegL = 0x22
    Reserved21 = 0x23
    ModWidthReg = 0x24
    Reserved22 = 0x25
    RFCfgReg = 0x26
    GsNReg = 0x27
    CWGsPReg = 0x28
    ModGsPReg = 0x29
    TModeReg = 0x2A
    TPrescalerReg = 0x2B
    TReloadRegH = 0x2C
    TReloadRegL = 0x2D
    TCounterValueRegH = 0x2E
    TCounterValueRegL = 0x2F

    Reserved30 = 0x30
    TestSel1Reg = 0x31
    TestSel2Reg = 0x32
    TestPinEnReg = 0x33
    TestPinValueReg = 0x34
    TestBusReg = 0x35
    AutoTestReg = 0x36
    VersionReg = 0x37
    AnalogTestReg = 0x38
    TestDAC1Reg = 0x39
    TestDAC2Reg = 0x3A
    TestADCReg = 0x3B
    Reserved31 = 0x3C
    Reserved32 = 0x3D
    Reserved33 = 0x3E
    Reserved34 = 0x3F

    serNum = []

    def __init__(self, bus=0, device=0, spd=1000000, pin_mode=10, pin_rst=-1, debugLevel='INFO'):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = spd

        self.logger = logging.getLogger('mfrc522Logger')
        self.logger.addHandler(logging.StreamHandler())
        level = logging.getLevelName(debugLevel)
        self.logger.setLevel(level)

        gpioMode = GPIO.getmode()
        
        if gpioMode is None:
            GPIO.setmode(pin_mode)
        else:
            pin_mode = gpioMode
            
        if pin_rst == -1:
            if pin_mode == 11: #BMC mode
                pin_rst = 24
            else:
                pin_rst = 18 #board
            
        GPIO.setup(pin_rst, GPIO.OUT)
        GPIO.output(pin_rst, 1)
        self.MFRC522_Init()

    def MFRC522_Reset(self):
        self.Write_MFRC522(self.CommandReg, self.PCD_RESETPHASE)

    def Write_MFRC522(self, addr, val):
        val = self.spi.xfer2([(addr << 1) & 0x7E, val]) # Bit [7]r/w [1:6]address [0]0

    def Read_MFRC522(self, addr):
        val = self.spi.xfer2([((addr << 1) & 0x7E) | 0x80, 0]) # Bit [7]r/w [1:6]address [0]0
        return val[1]

    def Close_MFRC522(self):
        self.spi.close()
        GPIO.cleanup()

    def SetBitMask(self, reg, mask):
        tmp = self.Read_MFRC522(reg)
        self.Write_MFRC522(reg, tmp | mask)

    def ClearBitMask(self, reg, mask):
        tmp = self.Read_MFRC522(reg)
        self.Write_MFRC522(reg, tmp & (~mask))

    def AntennaOn(self):
        temp = self.Read_MFRC522(self.TxControlReg)
        if (~(temp & 0x03)):
            self.SetBitMask(self.TxControlReg, 0x03)

    def AntennaOff(self):
        self.ClearBitMask(self.TxControlReg, 0x03)

#Writes the command to the commad register. 
    def MFRC522_ToCard(self, command, sendData):
        backData = []
        backLen = 0
        status = self.MI_ERR
        irqEn = 0x00
        waitIRq = 0x00
        lastBits = None
        n = 0

        if command == self.PCD_AUTHENT:
            irqEn = 0x12
            waitIRq = 0x10
        if command == self.PCD_TRANSCEIVE:
            irqEn = 0x77   #TimerIRq, errIRq, loAlertIRq, idleIrq, RxIrq, TxIRq enable (reg 0x02)
            waitIRq = 0x30 #command terminates or RX end of valid data stream.

        self.Write_MFRC522(self.CommIEnReg, irqEn | 0x80)   # Reg 0x04, irq mask | 0x80 invert IRQ pin with respect to status1reg IRQ but
        self.ClearBitMask(self.CommIrqReg, 0x80)            # indicates that the marked bits in the ComIrqReg register are set       
        self.SetBitMask(self.FIFOLevelReg, 0x80)            # Flush FIFO buffer  

        self.Write_MFRC522(self.CommandReg, self.PCD_IDLE)  #command reg idle / Cancels currnt command execution. 

        for i in range(len(sendData)):
            self.Write_MFRC522(self.FIFODataReg, sendData[i]) #set data to be sent

        self.Write_MFRC522(self.CommandReg, command) #set the command

        if command == self.PCD_TRANSCEIVE: 
            self.SetBitMask(self.BitFramingReg, 0x80) #start the command if type transceive. (Other commands start immediately)

        i = 2000
        while True:
            n = self.Read_MFRC522(self.CommIrqReg)  #
            i -= 1
            if ~((i != 0) and ~(n & 0x01) and ~(n & waitIRq)): #if i = 0, irq = TCounterValReg = 0 = timeout, wait for specific irq. 
                break

        self.ClearBitMask(self.BitFramingReg, 0x80) #clear the start transmission of data (transceive command)

        if i != 0:
            if (self.Read_MFRC522(self.ErrorReg) & 0x1B) == 0x00:  #check for errors
                status = self.MI_OK

                if n & irqEn & 0x01:            #if IRQ = TimerIRq 
                    status = self.MI_NOTAGERR

                if command == self.PCD_TRANSCEIVE:
                    n = self.Read_MFRC522(self.FIFOLevelReg)               # n = FIFO level in bytes
                    lastBits = self.Read_MFRC522(self.ControlReg) & 0x07   #Read control reg. [0:2] num of valid bits in last byte. 000 = whole byte valid
                    if lastBits != 0:
                        backLen = (n - 1) * 8 + lastBits    #calculate num of valid bits?               
                    else:
                        backLen = n * 8

                    if n == 0:
                        n = 1
                    if n > self.MAX_LEN:
                        n = self.MAX_LEN

                    for i in range(n):
                        backData.append(self.Read_MFRC522(self.FIFODataReg)) #read n bytes from fifo. Decrements fifo counter. 
            else:
                status = self.MI_ERR

        return (status, backData, backLen)

    def MFRC522_Request(self, reqMode):
        status = None
        backBits = None
        TagType = []

        self.Write_MFRC522(self.BitFramingReg, 0x07)

        TagType.append(reqMode)
        (status, backData, backBits) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, TagType)

        if ((status != self.MI_OK) | (backBits != 0x10)):
            status = self.MI_ERR
        #self.logger.debug(f"[Request | mode data] {reqMode}  {backData}")
        return (status, backBits)

    def MFRC522_Anticoll(self, cascade_level):
        backData = []
        serNumCheck = 0

        serNum = [cascade_level, 0x20]

        self.Write_MFRC522(self.BitFramingReg, 0x00)

        # serNum.append(cascade_level)
        # serNum.append(0x20)

        (status, backData, backBits) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, serNum)

        self.logger.debug(f"[Anticoll (CL) (DA)] {cascade_level}  {backData}")

        if (status == self.MI_OK):
            i = 0
            if len(backData) == 5:
                for i in range(4):
                    serNumCheck = serNumCheck ^ backData[i] 
                if serNumCheck != backData[4]: #Check Sum 
                    self.logger.debug(f"[Anticoll] CHECKSUM ERROR {serNumCheck}")
                    status = self.MI_ERR
            else:
                self.logger.debug(f"[Anticoll] DATA LENGTH ERROR {backBits}")
                status = self.MI_ERR

        return (status, backData)

    def MFRC522_SelectTag(self, serNum, cascade_level):
        backData = []
        buf = [cascade_level, 0x70 ]
        
        for i in range(5):
            buf.append(serNum[i])

        pOut = self.CalulateCRC(buf)
        buf.append(pOut[0])
        buf.append(pOut[1])
        (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, buf)
        
        self.logger.debug(f"[Select Tag] {cascade_level} {backData}")

        if (status == self.MI_OK) and (backLen == 0x18):
            return backData[0]
        else:
            return 0

    def CalulateCRC(self, pIndata):
        self.ClearBitMask(self.DivIrqReg, 0x04)
        self.SetBitMask(self.FIFOLevelReg, 0x80)

        for i in range(len(pIndata)):
            self.Write_MFRC522(self.FIFODataReg, pIndata[i])

        self.Write_MFRC522(self.CommandReg, self.PCD_CALCCRC)
        i = 0xFF
        while True:
            n = self.Read_MFRC522(self.DivIrqReg)
            i -= 1
            if not ((i != 0) and not (n & 0x04)):
                break
        pOutData = []
        pOutData.append(self.Read_MFRC522(self.CRCResultRegL))
        pOutData.append(self.Read_MFRC522(self.CRCResultRegM))
        return pOutData

    def MFRC522_StopCrypto1(self):
        self.ClearBitMask(self.Status2Reg, 0x08)

    def MFRC522_GetVersion(self):
        recvData = []
        recvData.append(self.PICC_GETVERSION) #0x30 read command
        pOut = self.CalulateCRC(recvData) #2 byte CRC
        recvData.append(pOut[0])
        recvData.append(pOut[1])
        (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, recvData) 
        if not (status == self.MI_OK):
            self.logger.error(f"[Get Version] Error while reading {status}")

        if len(backData) == 10:
            self.logger.debug(f"[Get Version Data]  {backData}")
            return backData
        else:
            self.logger.warning(f"[Get Version Error]  {backLen}  {backData}")
            return None

    def MFRC522_Read(self, blockAddr):
        recvData = []
        recvData.append(self.PICC_READ) #0x30 read command
        recvData.append(blockAddr)      # page to read, receives back 4 pages = 16bytes 
        pOut = self.CalulateCRC(recvData) #2 byte CRC
        recvData.append(pOut[0])
        recvData.append(pOut[1])
        (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, recvData) #0x0C
        if not (status == self.MI_OK):
            self.logger.error(f"[READ] Error while reading {status}")

        if len(backData) == 16:
            self.logger.debug(f"[READ (Sector) (Data)] {blockAddr}  {backData}")
            return backData
        else:
            return None

    def MFRC522_Write(self, blockAddr, writeData):
        buff = []
        buff.append(self.PICC_WRITE)
        buff.append(blockAddr)
        crc = self.CalulateCRC(buff)
        buff.append(crc[0])
        buff.append(crc[1])
        (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, buff)
        if not (status == self.MI_OK) or not (backLen == 4) or not ((backData[0] & 0x0F) == 0x0A):
            status = self.MI_ERR
            print("Error sending command")
        self.logger.debug("%s backdata &0x0F == 0x0A %s" % (backLen, backData[0] & 0x0F))
        if status == self.MI_OK:
            buf = []
            for i in range(16):
                print("Data: " + ascii(writeData[i]) + "i: " + str(i))
                buf.append(writeData[i])

            crc = self.CalulateCRC(buf)
            buf.append(crc[0])
            buf.append(crc[1])
            (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, buf)
            if not (status == self.MI_OK) or not (backLen == 4) or not ((backData[0] & 0x0F) == 0x0A):
                self.logger.error("Error while writing")
            if status == self.MI_OK:
                self.logger.debug("Data written")

        # def  MFRC522_Auth(self, authMode, BlockAddr, Sectorkey, serNum):
    
    
    #     buff = []

    #     # First byte should be the authMode (A or B)
    #     buff.append(authMode)

    #     # Second byte is the trailerBlock (usually 7)
    #     buff.append(BlockAddr)

    #     # Now we need to append the authKey which usually is 6 bytes of 0xFF
    #     for i in range(len(Sectorkey)):
    #         buff.append(Sectorkey[i])

    #     # Next we append the first 4 bytes of the UID
    #     for i in range(4):
    #         buff.append(serNum[i])

    #     # Now we start the authentication itself
    #     (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_AUTHENT, buff)

    #     # Check if an error occurred
    #     if not (status == self.MI_OK):
    #         self.logger.error("AUTH ERROR!!")
    #     if not (self.Read_MFRC522(self.Status2Reg) & 0x08) != 0:
    #         self.logger.error("AUTH ERROR(status2reg & 0x08) != 0")

    #     # Return the status
    #     return status

    # def MFRC522_DumpClassic1K(self, key, uid):
    #     for i in range(64):
    #         status = self.MFRC522_Auth(self.PICC_AUTHENT1A, i, key, uid)
    #         # Check if authenticated
    #         if status == self.MI_OK:
    #             self.MFRC522_Read(i)
    #         else:
    #             self.logger.error("Authentication error")


    def MFRC522_Init(self):
        self.MFRC522_Reset()

        self.Write_MFRC522(self.TModeReg, 0x8D)
        self.Write_MFRC522(self.TPrescalerReg, 0x3E)
        self.Write_MFRC522(self.TReloadRegL, 30)
        self.Write_MFRC522(self.TReloadRegH, 0)

        self.Write_MFRC522(self.TxAutoReg, 0x40)
        self.Write_MFRC522(self.ModeReg, 0x3D)
        self.AntennaOn()
