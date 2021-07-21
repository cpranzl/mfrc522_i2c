#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""
Fills datablocks with random values
"""

__author__ = "Christoph Pranzl"
__version__ = "0.0.1"
__license__ = "GPLv3"

from mfrc522_i2c import MFRC522
import random

continue_reading = True

# Create random data
def random_data(size=16):
    data = []
    for i in range(size):
        data.append(random.randint(0, 255))
    return (data)

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
            print(f'Card identified, UID: {uid[0]}{uid[1]}{uid[2]}{uid[3]}')

            # Select the scanned card
            (status, backData, backBits) = MFRC522Reader.select(uid)
            if status == MFRC522Reader.MI_OK:
                print('Card selected')

                # Authenticate
                mode = MFRC522Reader.MIFARE_AUTHKEY1
                blockAddr = 8
                key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

                for blockAddr in MFRC522Reader.MIFARE_1K_DATABLOCK:
                    (status, backData, backBits) = MFRC522Reader.authenticate(
                        mode,
                        blockAddr,
                        key,
                        uid)

                    if (status == MFRC522Reader.MI_OK):

                        # Write new data to card
                        data = random_data()
                        (status, backData, backBits) = MFRC522Reader.write(
                            blockAddr,
                            data)
                        if (status == MFRC522Reader.MI_OK):
                            print(f'Data  {blockAddr:02} ', end = '')
                            for i in range(0,16):
                                print(f'{data[i]:02x} ', end = '')
                            print()
                        else:
                            print('Error while writing new data')

                        continue_reading = False

                    else:
                        print('Authentication error')

            # Deauthenticate
            MFRC522Reader.deauthenticate()