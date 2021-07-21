#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""
Scans countinously for cards and prints the UID
"""

__author__ = "Christoph Pranzl"
__version__ = "0.0.1"
__license__ = "GPLv3"

from mfrc522_i2c import MFRC522
import signal

continue_reading = True


# Capture SIGINT for cleanup when script is aborted
def end_read(signal, frame):
    global continue_reading
    print('Ctrl+C captured, ending read')
    continue_reading = False


# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

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