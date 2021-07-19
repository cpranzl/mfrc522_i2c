#!/usr/bin/env python3
# -*- coding: utf8 -*-

import MFRC522
import signal

continue_reading = True

# Create an object of the class MFRC
MFRC522Reader = MFRC522.MFRC522()

MFRC522Reader.showReaderDetails()

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

                # Authenticate
                mode = MFRC522Reader.MIFARE_AUTHKEY1
                blockAddr = 0

                for blockAddr in MFRC522Reader.MIFARE_USERDATA:
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