#!/usr/bin/env python3
# -*- coding: utf8 -*-

from smbus import SMBus


class MFRC522:
    # Define register values from datasheet
    # Page 0: Command & Status register
    COMMANDREG = 0x01  # Start and stops command execution
    COMIENREG = 0x02  # Enable and disable interrupt request control bits
    COMIRQREG = 0x04  # Interrupt request bits
    DIVIRQREG = 0x05  # Interrupt request bits
    ERRORREG = 0x06  # Error bits showing the error status of the last command
    STATUS2REG = 0x08  # Receiver and transmitter status bits
    FIFODATAREG = 0x09  # Input and output of 64 byte FIFO buffer
    FIFOLEVELREG = 0x0A  # Number of bytes stored in the FIFO buffer
    CONTROLREG = 0x0C  # Miscellaneous control register
    BITFRAMINGREG = 0x0D  # Adjustments for bit-oriented frames
    # Page 1: Command register
    MODEREG = 0x11  # Defines general modes for transmitting and receiving
    TXCONTROLREG = 0x14  # Controls the logical behavior of the antenna
    # driver pins
    TXASKREG = 0x15  # Controls the setting of the transmission modulation
    # Page 2: Configuration register
    CRCRESULTREGMSB = 0x21  # Shows the MSB of the CRC calculation
    CRCRESULTREGLSB = 0x22  # Shows the LSB of the CRC calculation
    TMODEREG = 0x2A  # Defines settings for the internal timer
    TPRESCALERREG = 0x2B  # Defines settings for internal timer
    TRELOADREGH = 0x2C  # Defines 16-bit timer reload value
    TRELOADREGL = 0x2D  # Defines 16-bit timer reload value
    # Page 3: Test register
    VERSIONREG = 0x37  # Shows the software version

    # MFRC522 Commands
    MFRC522_IDLE = 0x00  # No actions, cancels current command execution
    MFRC522_CALCCRC = 0x03  # Activates the CRC coprocessor and performs
    # a self test
    MFRC522_TRANSCEIVE = 0x0C  # Transmits data from FIFO buffer to
    # anntenna and automatically activates the receiver after
    # transmission
    MFRC522_MFAUTHENT = 0x0E  # Performs the MIFARE standard authentication
    # as a reader
    MFRC522_SOFTRESET = 0x0F  # Resets the MFRC522

    # MIFARE Classic Commands
    MIFARE_REQUEST = [0x26]
    MIFARE_WAKEUP = [0x52]
    MIFARE_ANTICOLCL1 = [0x93, 0x20]
    MIFARE_SELECTCL1 = [0x93, 0x70]
    MIFARE_ANTICOLCL2 = [0x95, 0x20]
    MIFARE_SELECTCL2 = [0x95, 0x70]
    MIFARE_HALT = [0x50, 0x00]
    MIFARE_AUTHKEY1 = [0x60]
    MIFARE_AUTHKEY2 = [0x61]
    MIFARE_READ = [0x30]
    MIFARE_WRITE = [0xA0]
    MIFARE_DECREMENT = [0xC0]
    MIFARE_INCREMENT = [0xC1]
    MIFARE_RESTORE = [0xC2]
    MIFARE_TRANSFER = [0xB0]

    MIFARE_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

    MIFARE_USERDATA = [ 1,  2,  4,  5,  6,  8,  9, 10, 12, 13, 14, 16, 17, 18,
                       20, 21, 22, 24, 25, 26, 28, 29, 30, 32, 33, 34, 36, 37,
                       38, 40, 41, 42, 44, 45, 46, 48, 49, 50, 52, 53, 54, 56,
                       57, 58, 60, 61, 62]

    MI_OK = 0
    MI_NOTAGERR = 1
    MI_ERR = 2

    MAX_LEN = 16

    i2cbus = SMBus(1)
    i2caddress = 0x28

    def __init__(self):
        self.MFRC522_init()

    def showReaderDetails(self):
        version = self.MFRC522_read(self.VERSIONREG)
        if (version == 0x91):
            print(f'MFRC522 Software Version: 0x{version:02x} = v1.0')
        if (version == 0x92):
            print(f'MFRC522 Software Version: 0x{version:02x} = v2.0')

    def scan(self):
        status = None
        backData = []
        backBits = None

        # None bits of the last byte
        self.MFRC522_write(self.BITFRAMINGREG, 0x07)

        buffer = []
        buffer.extend(self.MIFARE_REQUEST)

        (status, backData, backBits) = self.transceiveCard(buffer)

        if ((status != self.MI_OK) | (backBits != 0x10)):
            status = self.MI_ERR

        return (status, backData, backBits)

    def serialNumberValid(self, serialNumber):
        i = 0
        serialCheck = 0

        while (i < (len(serialNumber) - 1)):
            serialCheck = serialCheck ^ serialNumber[i]
            i = i + 1
        if (serialCheck != serialNumber[i]):
            return False
        else:
            return True

    def transceive(self):
        status = None
        backData = []
        backBits = None

        # All bits of the last byte
        self.MFRC522_write(self.BITFRAMINGREG, 0x00)

        buffer = []
        buffer.extend(self.MIFARE_ANTICOLCL1)

        (status, backData, backBits) = self.transceiveCard(buffer)

        if (status == self.MI_OK):
            if (self.serialNumberValid(backData)):
                status = self.MI_OK
            else:
                status = self.MI_ERR

        return (status, backData, backBits)

    def transceiveCard(self, data):
        status = None
        backData = []
        backBits = None

        IRqInv = 0x80  # Signal on pin IRQ is inverted
        TxIEn = 0x40  # Allow the transmitter to interrupt requests
        RxIEn = 0x20  # Allow the receiver to interrupt requests
        IdleIEn = 0x10  # Allow the idle interrupt request
        LoAlertIEn = 0x04  # Allow the low Alert interrupt request
        ErrIEn = 0x02  # Allow the error interrupt request
        TimerIEn = 0x01  # Allow the timer interrupt request
        self.MFRC522_write(self.COMIENREG, (IRqInv |
                                            TxIEn |
                                            RxIEn |
                                            IdleIEn |
                                            LoAlertIEn |
                                            ErrIEn |
                                            TimerIEn))

        # Indicates that the bits in the ComIrqReg register are set
        Set1 = 0x80
        self.MFRC522_clearBitMask(self.COMIRQREG, Set1)

        # Immediatly clears the internal FIFO buffer's read and write pointer
        # and ErrorReg register's BufferOvfl bit
        FlushBuffer = 0x80
        self.MFRC522_setBitMask(self.FIFOLEVELREG, FlushBuffer)

        # Cancel running commands
        self.MFRC522_write(self.COMMANDREG, self.MFRC522_IDLE)

        # Write data in FIFO register
        i = 0
        while (i < len(data)):
            self.MFRC522_write(self.FIFODATAREG, data[i])
            i = i + 1

        # Countinously repeat the transmission of data from the FIFO buffer and
        # the reception of data from the RF field.
        self.MFRC522_write(self.COMMANDREG, self.MFRC522_TRANSCEIVE)

        # Starts the transmission of data, only valid in combination with the
        # Transceive command
        StartSend = 0x80
        self.MFRC522_setBitMask(self.BITFRAMINGREG, StartSend)

        # The timer has decrement the value in TCounterValReg register to zero
        TimerIRq = 0x01
        # The receiver has detected the end of a valid data stream
        RxIRq = 0x20
        # A command was terminated or unknown command is started
        IdleIRq = 0x10

        # Wait for an interrupt
        i = 2000
        while True:
            comIRqReg = self.MFRC522_read(self.COMIRQREG)
            if (comIRqReg & TimerIRq):
                # Timeout
                break
            if (comIRqReg & RxIRq):
                # Valid data available in FIFO
                break
            if (comIRqReg & IdleIRq):
                # Command terminate
                break
            if (i == 0):
                # Watchdog expired
                break

        # Clear the StartSend bit in BitFramingReg register
        self.MFRC522_clearBitMask(self.BITFRAMINGREG, StartSend)

        # Retrieve data from FIFODATAREG
        if (i != 0):
            # The host or a MFRC522's internal state machine tries to write
            # data to the FIFO buffer even though it is already full
            BufferOvfl = 0x10
            # A bit collision is detected
            ColErr = 0x08
            # Parity check failed
            ParityErr = 0x02
            # Set to logic 1 if the SOF is incorrect
            ProtocolErr = 0x01

            errorTest = (BufferOvfl | ColErr | ParityErr | ProtocolErr)
            errorReg = self.MFRC522_read(self.ERRORREG)

            # Test if any of the errors above happend
            if (~(errorReg & errorTest)):
                status = self.MI_OK

                # Indicates any error bit in thr ErrorReg register is set
                ErrIRq = 0x02

                # Test if the timer expired and an error occured
                if (comIRqReg & TimerIRq & ErrIRq):
                    status = self.MI_NOTAGERR

                fifoLevelReg = self.MFRC522_read(self.FIFOLEVELREG)

                # Edge cases
                if fifoLevelReg == 0:
                    fifoLevelReg = 1
                if fifoLevelReg > self.MAX_LEN:
                    fifoLevelReg = self.MAX_LEN

                # Indicates the number of valid bits in the last received byte
                RxLastBits = 0x08

                lastBits = self.MFRC522_read(self.CONTROLREG) & RxLastBits

                if (lastBits != 0):
                    backBits = (fifoLevelReg - 1) * 8 + lastBits
                else:
                    backBits = fifoLevelReg * 8

                i = 0
                while (i < fifoLevelReg):
                    backData.append(self.MFRC522_read(self.FIFODATAREG))
                    i = i + 1

            else:
                status.MI_ERR

        return (status, backData, backBits)

    def calculateCRC(self, data):
        # Clear the bit that indicates taht the CalcCRC command is active
        # and all data is processed
        CRCIRq = 0x04
        self.MFRC522_clearBitMask(self.DIVIRQREG, CRCIRq)

        # Immedialty clears the internal FIFO buffer's read and write pointer
        # and ErrorReg register's BufferOvfl bit
        FlushBuffer = 0x80
        self.MFRC522_setBitMask(self.FIFOLEVELREG, FlushBuffer)

        # Write data to FIFO
        i = 0
        while (i < len(data)):
            self.MFRC522_write(self.FIFODATAREG, data[i])
            i = i + 1

        # Execute CRC calculation
        self.MFRC522_write(self.COMMANDREG, self.MFRC522_CALCCRC)
        i = 255
        while True:
            divirqreg = self.MFRC522_read(self.DIVIRQREG)
            i = i - 1
            if (i == 0):
                # Watchdog expired
                break
            if (divirqreg & CRCIRq):
                # CRC is calculated
                break

        # Retrieve CRC from CRCRESULTREG
        crc = []
        crc.append(self.MFRC522_read(self.CRCRESULTREGLSB))
        crc.append(self.MFRC522_read(self.CRCRESULTREGMSB))

        return (crc)

    def select(self, serialNumber):
        status = None
        backData = []
        backBits = None

        buffer = []
        buffer.extend(self.MIFARE_SELECTCL1)

        i = 0
        while (i < 5):
            buffer.append(serialNumber[i])
            i = i + 1

        crc = self.calculateCRC(buffer)
        buffer.extend(crc)

        (status, backData, backBits) = self.transceiveCard(buffer)

        return (status, backData, backBits)

    def authenticate(self, mode, blockAddr, key, serialNumber):
        status = None
        backData = []
        backBits = None

        buffer = []
        buffer.extend(mode)
        buffer.append(blockAddr)
        buffer.extend(key)

        i = 0
        while (i < 4):
            buffer.append(serialNumber[i])
            i = i + 1

        (status, backData, backBits) = self.authenticateCard(buffer)

        return (status, backData, backBits)

    def deauthenticate(self):
        # Indicates that the MIFARE Crypto1 unit is switched on and
        # therfore all data communication with the card is encrypted
        # Can ONLY be set to logic 1 by a successfull execution of
        # the MFAuthent command
        MFCrypto1On = 0x08
        self.MFRC522_clearBitMask(self.STATUS2REG, MFCrypto1On)

    def authenticateCard(self, data):
        status = None
        backData = []
        backBits = None

        IRqInv = 0x80  # Signal on pin IRQ is inverted
        IdleIEn = 0x10  # Allow the idle interrupt request
        ErrIEn = 0x02  # Allow the error interrupt request
        self.MFRC522_write(self.COMIENREG, (IRqInv | IdleIEn | ErrIEn))

        # Indicates that the bits in the ComIrqReg register are set
        Set1 = 0x80
        self.MFRC522_clearBitMask(self.COMIRQREG, Set1)

        # Immedialty clears the interl FIFO buffer's read and write pointer
        # and ErrorReg register's BufferOvfl bit
        FlushBuffer = 0x80
        self.MFRC522_setBitMask(self.FIFOLEVELREG, FlushBuffer)

        # Cancel running commands
        self.MFRC522_write(self.COMMANDREG, self.MFRC522_IDLE)

        # Write data in FIFO register
        i = 0
        while (i < len(data)):
            self.MFRC522_write(self.FIFODATAREG, data[i])
            i = i + 1

        # This command manages MIFARE authentication to anable a secure
        # communication to any MIFARE card
        self.MFRC522_write(self.COMMANDREG, self.MFRC522_MFAUTHENT)

        # The timer has decrement the value in TCounterValReg register to zero
        TimerIRq = 0x01
        # The receiver has detected the end of a valid data stream
        RxIRq = 0x20
        # A command was terminated or unknown command is started
        IdleIRq = 0x10

        # Wait for an interrupt
        i = 2000
        while True:
            comIRqReg = self.MFRC522_read(self.COMIRQREG)
            if (comIRqReg & TimerIRq):
                # Timeout
                break
            if (comIRqReg & RxIRq):
                # Valid data available in FIFO
                break
            if (comIRqReg & IdleIRq):
                # Command terminate
                break
            if (i == 0):
                # Watchdog expired
                break

        # Clear the StartSend bit in BitFramingReg register
        StartSend = 0x80
        self.MFRC522_clearBitMask(self.BITFRAMINGREG, StartSend)

        # Retrieve data from FIFODATAREG
        if (i != 0):
            # The host or a MFRC522's internal state machine tries to write
            # data to the FIFO buffer even though it is already full
            BufferOvfl = 0x10
            # A bit collision is detected
            ColErr = 0x08
            # Parity check failed
            ParityErr = 0x02
            # Set to logic 1 if the SOF is incorrect
            ProtocolErr = 0x01

            errorTest = (BufferOvfl | ColErr | ParityErr | ProtocolErr)
            errorReg = self.MFRC522_read(self.ERRORREG)

            # Test if any of the errors above happend
            if (~(errorReg & errorTest)):
                status = self.MI_OK

                # Indicates any error bit in thr ErrorReg register is set
                ErrIRq = 0x02

                # Test if the timer expired and an error occured
                if (comIRqReg & TimerIRq & ErrIRq):
                    status = self.MI_NOTAGERR

            else:
                status = self.MI_ERR

        return (status, backData, backBits)

    def read(self, blockAddr):
        status = None
        backData = []
        backBits = None

        buffer = []
        buffer.extend(self.MIFARE_READ)
        buffer.append(blockAddr)

        crc = self.calculateCRC(buffer)
        buffer.extend(crc)

        (status, backData, backBits) = self.transceiveCard(buffer)

        return (status, backData, backBits)

    def write(self, blockAddr, data):
        status = None
        backData = []
        backBits = None

        buffer = []
        buffer.extend(self.MIFARE_WRITE)
        buffer.append(blockAddr)

        crc = self.calculateCRC(buffer)
        buffer.extend(crc)

        (status, backData, backBits) = self.transceiveCard(buffer)

        if (status == self.MI_OK):

            buffer.clear()
            buffer.extend(data)

            crc = self.calculateCRC(buffer)
            buffer.extend(crc)

            (status, backData, backBits) = self.transceiveCard(buffer)

        return (status, backData, backBits)

    def MFRC522_antennaOn(self):
        value = self.MFRC522_read(self.TXCONTROLREG)
        if (~(value & 0x03)):
            self.MFRC522_setBitMask(self.TXCONTROLREG, 0x03)

    def MFRC522_antennaOff(self):
        self.MFRC522_clearBitMask(self.TXCONTROLREG, 0x03)

    def MFRC522_reset(self):
        self.MFRC522_write(self.COMMANDREG, self.MFRC522_SOFTRESET)

    def MFRC522_init(self):
        self.MFRC522_reset()

        self.MFRC522_write(self.TMODEREG, 0x8D)
        self.MFRC522_write(self.TPRESCALERREG, 0x3E)
        self.MFRC522_write(self.TRELOADREGL, 30)
        self.MFRC522_write(self.TRELOADREGH, 0)

        self.MFRC522_write(self.TXASKREG, 0x40)
        self.MFRC522_write(self.MODEREG, 0x3D)

        self.MFRC522_antennaOn()

    def MFRC522_read(self, address):
        value = self.i2cbus.read_byte_data(self.i2caddress, address)
        return value

    def MFRC522_write(self, address, value):
        self.i2cbus.write_byte_data(self.i2caddress, address, value)

    def MFRC522_setBitMask(self, address, mask):
        value = self.MFRC522_read(address)
        self.MFRC522_write(address, value | mask)

    def MFRC522_clearBitMask(self, address, mask):
        value = self.MFRC522_read(address)
        self.MFRC522_write(address, value & (~mask))
