#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""
Dumps datablocks
"""

__author__ = "Christoph Pranzl"
__version__ = "0.0.1"
__license__ = "GPLv3"

from mfrc522_i2c import MFRC522
import signal

continue_reading = True

# Create an object of the class MFRC
MFRC522Reader = MFRC522.MFRC522()

version = MFRC522Reader.getReaderVersion()
print(f'MFRC522 Software Version: {version}')

while continue_reading:
    # Scan for cards
    (status, backData, tagType) = MFRC522Reader.scan()
    if status == MFRC522Reader.MI_OK:
        print(f'Card detected, Type: {tagType}')

        # Get UID of the card
        (status, uid, backBits) = MFRC522Reader.transceive()
        if status == MFRC522Reader.MI_OK:
            print(f'Card identified, '
                  f'UID: {uid[0]:02x}:{uid[1]:02x}:{uid[2]:02x}:{uid[3]:02x}')

            # Select the scanned card
            (status, backData, backBits) = MFRC522Reader.select(uid)
            if status == MFRC522Reader.MI_OK:
                print('Card selected')

                # TODO: Determine 1K or 4K

                # Authenticate
                mode = MFRC522Reader.MIFARE_AUTHKEY1
                
                blockAddr = 0
                for blockAddr in MFRC522Reader.MIFARE_1K_DATABLOCK:
                    (status, backData, backBits) = MFRC522Reader.authenticate(
                        mode,
                        blockAddr,
                        MFRC522Reader.MIFARE_KEY,
                        uid)
                    if (status == MFRC522Reader.MI_OK):
                        
                        (status, backData, backBits) = MFRC522Reader.read(
                            blockAddr)
                        if (status == MFRC522Reader.MI_OK):
                            print(f'Block {blockAddr:02} ', end = '')
                            for i in range(0,16):
                                print(f'{backData[i]:02x} ', end = '')
                            print()
                        
                        else:
                            print('Error while reading')
                    
                        continue_reading = False
                        
                    else:
                        print('Authentication error')

                # Deauthenticate
                MFRC522Reader.deauthenticate()
                print('Card deauthenticated')