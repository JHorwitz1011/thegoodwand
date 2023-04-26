
# Code by Simon Monk https://github.com/simonmonk/

from ast import Constant
from . import MFRC522
import RPi.GPIO as GPIO
import math
import time

NTAG13_STORAGE = 0X0F
NTAG15_STORAGE = 0X11
NTAG16_STORAGE = 0X13

#BYTES = NUM_BLOCKS * 4PAGES/BLOCK * 4BYTES/PAGE 
NTAG13_USER_BLOCK_SIZE = 9 # 9*4*4 = 144BYTES
NTAG15_USER_BLOCK_SIZE = 32 # 31*4*4 = 512  (Last 8 bytes protected)
NTAG16_USER_BLOCK_SIZE = 56 # 55*4*4 = 880BYTES  (+8)
USER_BLOCK_SIZE_MIN    = 3 # 3*4*4 48 bytes

USER_MEMORY_POS = 4  #STARTING BLOCK FOR USER MEMEORY
PAGES_PER_BLOCK = 4
class SimpleMFRC522:



    def __init__(self):
        self.READER = MFRC522()


    def read(self, delay):
        id, text = self.read_block()
        while not id:
            id, text = self.read_block()
            time.sleep(delay)
        return id, text

    

    def read_block(self):
        status, uid = self.select_tag()
        if status != self.READER.MI_OK:
            return None, None
        
        card_size = self.get_card_size()

        #Failed to read card size. reselect tag and read the minumum
        if card_size == 0: 
            status, uid = self.select_tag()
            if status != self.READER.MI_OK:
                return None, None
            card_size = USER_BLOCK_SIZE_MIN
        
        data = []
        text_read = ''
        
        if status == self.READER.MI_OK:
            for i in range(card_size): 
                page_address = USER_MEMORY_POS + (i * PAGES_PER_BLOCK)
                self.READER.logger.debug(f"[PAGE ADDRESS] {page_address}")
                block = self.READER.MFRC522_Read(page_address)
                if block:
                    data += block
                else:
                    self.READER.logger.debug(f"[READ BLOCK] READ ERROR") #If there is a read error return 
                    #uid = None
                    break
                if data:
                    text_read = ''.join(chr(i) for i in data)
        self.READER.MFRC522_StopCrypto1()
        return uid, text_read

    # def write(self, text):
    #     id, text_in = self.write_no_block(text)
    #     while not id:
    #         id, text_in = self.write_no_block(text)
    #     return id, text_in

    
    # #TODO clear memory on wirte and check size based on card size. 
    # def write_no_block(self, text):
    #     status, uid = self.select_tag()
    #     if status != self.READER.MI_OK:
    #         return None, None

    #     self.READER.MFRC522_Read(11)
    #     if status == self.READER.MI_OK:
    #         #data = bytearray()
    #         #data.extend(bytearray(text.ljust(len(self.BLOCK_ADDRS) * 16).encode('ascii')))
    #         # how many 4 byte blocks do we need.
    #         block_count = math.ceil(len(text)/4)
    #         self.READER.logger.debug("WRITE:numblocks needed: " + str(block_count))
    #         if block_count > self.MAX_BLOCK:
    #             return id, "Too Large"
    #         i = 0
    #         for block_num in range(block_count):
    #             block_num += self.USER_BLOCK_START
    #             self.READER.logger.debug("Writing Block " + str(block_num))
    #             # using compadibility write. Writes 16 bytes but on 4 are stored on the tag
    #             self.READER.MFRC522_Write(block_num, bytearray(
    #                 text[i*4:(i+1)*4], 'ascii').ljust(16))
    #             i += 1
    #     self.READER.MFRC522_StopCrypto1()
    #     return uid, text[0:(len(self.BLOCK_ADDRS) * 16)]


    def get_version(self):
        while (True):
            status, uid = self.select_tag()
            if status == self.READER.MI_OK:
                break
        return self.READER.MFRC522_GetVersion()

    #returns the card size in blocks (1 Block = 4 pages = 16Bytes)
    def get_card_size(self):

        version = self.READER.MFRC522_GetVersion()
        card_size = 0
        
        self.READER.logger.debug(f"[GET SIZE] {version}")
        
        if version:
            if version [6] == NTAG13_STORAGE:
                card_size = NTAG13_USER_BLOCK_SIZE
            
            elif version [6] == NTAG15_STORAGE:
                card_size = NTAG15_USER_BLOCK_SIZE
            
            elif version [6] == NTAG16_STORAGE:
                card_size = NTAG16_USER_BLOCK_SIZE
            
        self.READER.logger.debug(f"[CARD BLOCK SIZE] {card_size}")
        return card_size


    def uid_to_num(self, uid):
        n = 0
        for i in range(0, len(uid)):
            n = n * 256 + uid[i]
        return n
    
    def select_tag(self):
        #tag type tells us how many uid bytes there are 
        (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
        if status != self.READER.MI_OK:
            return status, None
        
        self.READER.logger.debug(f"[SELECT TAG] REQUEST ACK")
        
        cascade_level_command = 0x93
        
        uid = []
        while True:
            #if anticol bit 4 == 0x88 or error bail
            (status, res) = self.READER.MFRC522_Anticoll(cascade_level_command)
            
            if status != self.READER.MI_OK:
                self.READER.logger.debug(f"[SELECT TAG] ANTICOLL Error")
                return status, None
            
            if(res[0] != 0x88): #if not CL, then send final select  
                break
            uid.extend(res[1:4])
            self.READER.MFRC522_SelectTag(res, cascade_level_command)
            cascade_level_command += 0x02

        self.READER.MFRC522_SelectTag(res, cascade_level_command)
        
        uid.extend(res[0:4])
        id = self.uid_to_num(uid)

        return self.READER.MI_OK, id
         
    def format_uid(self, uid):
        id = ""
        for i in range(len(uid)):
            if i == 0: 
                id += '{0:02x}'.format(uid[i])
            else:
                id += ':' + '{0:02x}'.format(uid[i])

        return id.upper()

