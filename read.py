#!/usr/bin/env python3
# -*- coding: utf8 -*-

import MRFC522
import signal

continue_reading = True


# Capture SIGINT for cleanup when script is aborted
def end_read(signal, frame):
    global continue_reading
    print('Ctrl+C captured, ending read')
    continue_reading = False


# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class mrfc
MRFC522Reader = MRFC522.MRFC522()

MRFC522Reader.showReaderDetails()

while continue_reading:
    # Scan for cards
    (status, backData, tagType) = MRFC522Reader.scan()
    if status == MRFC522Reader.MI_OK:
        print(f'Card detected, Type: {tagType}')

        # Get UID of the card
        (status, uid, backBits) = MRFC522Reader.transceive()
        if status == MRFC522Reader.MI_OK:
            print(f'Card identified, '
                  f'UID: {uid[0]:02x}:{uid[1]:02x}:{uid[2]:02x}:{uid[3]:02x}')

            # Select the scanned card
            (status, backData, backBits) = MRFC522Reader.select(uid)
            if status == MRFC522Reader.MI_OK:
                print('Card selected')

                # Authenticate
                mode = MRFC522Reader.MIFARE_AUTHKEY1
                blockAddr = 8
                (status, backData, backBits) = MRFC522Reader.authenticate(
                    mode,
                    blockAddr,
                    MRFC522Reader.MIFARE_KEY,
                    uid)
                if (status == MRFC522Reader.MI_OK):
                    print('Card authenticated')

                    # Read data from card
                    (status, backData, backBits) = MRFC522Reader.read(
                        blockAddr)
                    if (status == MRFC522Reader.MI_OK):
                        print(f'Block {blockAddr:02} ', end = '')
                        for i in range(0,16):
                            print(f'{backData[i]:02x} ', end = '')
                        print()

                        continue_reading = False
                    else:
                        print('Error while reading')
                    
                    # Deauthenticate
                    MRFC522Reader.deauthenticate()
                    print('Card deauthenticated')
                else:
                    print('Authentication error')
