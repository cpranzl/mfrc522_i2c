#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""
Fills datablocks with random values
"""

__author__ = "Christoph Pranzl"
__version__ = "0.0.5"
__license__ = "GPLv3"

from mfrc522_i2c import MFRC522
import signal
import random


continue_reading = True


def end_read(signal, frame):
    """ Capture SIGINT for cleanup when script is aborted """
    global continue_reading
    print('Ctrl+C captured, ending read')
    continue_reading = False


def random_data(size=16):
    """ Create random data """
    data = []
    for i in range(size):
        data.append(random.randint(0, 255))
    return (data)


# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Reader is located at Bus 1, adress 0x28
i2cBus = 1
i2cAddress = 0x28

# Create an object of the class MFRC522
MFRC522Reader = MFRC522(i2cBus, i2cAddress)

version = MFRC522Reader.getReaderVersion()
print(f'MFRC522 Software Version: {version}')

while continue_reading:
    # Scan for cards
    (status, backData, tagType) = MFRC522Reader.scan()
    if status == MFRC522Reader.MIFARE_OK:
        print(f'Card detected, Type: {tagType}')

        # Get UID of the card
        (status, uid, backBits) = MFRC522Reader.identify()
        if status == MFRC522Reader.MIFARE_OK:
            print('Card identified, UID: ', end='')
            for i in range(0, len(uid) - 1):
                print(f'{uid[i]:02x}:', end='')
            print(f'{uid[len(uid) - 1]:02x}')

            # Select the scanned card
            (status, backData, backBits) = MFRC522Reader.select(uid)
            if status == MFRC522Reader.MIFARE_OK:
                print('Card selected')

                # TODO: Determine 1K or 4K

                # Authenticate
                for blockAddr in MFRC522Reader.MIFARE_1K_DATABLOCK:
                    (status, backData, backBits) = MFRC522Reader.authenticate(
                        MFRC522Reader.MIFARE_AUTHKEY1,
                        blockAddr,
                        MFRC522Reader.MIFARE_KEY,
                        uid)

                    if (status == MFRC522Reader.MIFARE_OK):

                        # Write new data to card
                        data = random_data()
                        (status, backData, backBits) = MFRC522Reader.write(
                            blockAddr,
                            data)
                        if (status == MFRC522Reader.MIFARE_OK):
                            print(f'Data  {blockAddr:02} : ', end='')
                            for i in range(0, len(data)):
                                print(f'{data[i]:02x} ', end='')
                            print('written')
                        else:
                            print('Error while writing new data')

                        continue_reading = False

                    else:
                        print('Authentication error')

                # Deauthenticate
                MFRC522Reader.deauthenticate()
