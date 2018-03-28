#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Title:    stick

    Author:   David Leclerc

    Version:  0.1

    Date:     27.03.2018

    License:  GNU General Public License, Version 3
              (http://www.gnu.org/licenses/gpl.html)

    Overview: This is a script that allows the creation of a Stick instance,
              which can be used to communicate with a Medtronic MiniMed insulin
              pump using a Texas Instruments CC1111 USB stick. It uses the PyUSB
              library and is based on the reverse-engineering of Carelink USB
              from Medtronic.

    Notes:    ...

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

# LIBRARIES
import usb



# USER LIBRARIES
import lib
import errors
import packets



# CLASSES
class Stick(object):

    def __init__(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Initialize stick properties.
        """

        # Initialize serial link
        self.link = None

        # Initialize configuration
        self.config = None

        # Initialize data endpoints
        self.EPs = {"OUT": None,
                    "IN": None}

        # Define USB IDs
        self.vendor = 0x0451
        self.product = 0x16A7

        # Define reference frequency (MHz)
        self.frequency = 24.0

        # Define commands
        self.commands = {"Product": 0,
                         "Author": 1,
                         "Register RX": 10,
                         "Register TX": 11,
                         "Radio RX": 20,
                         "Radio TX": 21,
                         "Radio TX/RX": 22,
                         "LED": 30,
                         "Test": 40}

        # Define registers
        self.registers = ["SYNC1", "SYNC0",
                          "PKTLEN",
                          "PKTCTRL1", "PKTCTRL0",
                          "ADDR", 
                          "FSCTRL1", "FSCTRL0",
                          "MDMCFG4", "MDMCFG3", "MDMCFG2", "MDMCFG1", "MDMCFG0",
                          "DEVIATN",
                          "MCSM2", "MCSM1", "MCSM0",
                          "BSCFG",
                          "FOCCFG",
                          "FREND1", "FREND0",
                          "FSCAL3", "FSCAL2", "FSCAL1", "FSCAL0",
                          "TEST1", "TEST0",
                          "PA_TABLE1", "PA_TABLE0",
                          "AGCCTRL2", "AGCCTRL1", "AGCCTRL0",
                          "FREQ2", "FREQ1", "FREQ0",
                          "CHANNR"]

        # Define errors
        self.errors = {"USB": {},
                       "Radio": {0xAA: "Timeout",
                                 0xBB: "No data"}}

        # Initialize bytes
        self.bytes = {"ID": None,
                      "RSSI": None,
                      "Payload": []}

        # Initialize packet
        self.packet = None



    def find(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            FIND
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Find the stick on the USB bus and link it.
        """

        # Find stick
        self.link = usb.core.find(idVendor = self.vendor,
                                  idProduct = self.product)

        # No stick found
        if self.link is None:

            # Raise error
            raise IOError("No stick found. Are you sure it's plugged in?")

        # Otherwise
        else:

            # Show stick
            print "Stick found."
            #print self.link



    def configure(self, f = 916.660):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            CONFIGURE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Configure the stick and assign EPs.
        """

        # Set configuration
        self.link.set_configuration()

        # Get configuration
        self.config = self.link.get_active_configuration()

        # Get EPs
        self.EPs["OUT"] = lib.getEP(self.config, "OUT")
        self.EPs["IN"] = lib.getEP(self.config, "IN")

        # Tune radio
        self.tune(f)



    def read(self, n = 64, timeout = 1000):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            READ
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Read from EP IN until it says it is done transmitting data using a
            zero byte. Timeout must be given in ms.
        """

        # Initialize bytes
        bytes = []

        # Read bytes
        while True:

            # Read, decode, and append new bytes
            bytes += self.EPs["IN"].read(n, timeout = timeout)

            # Exit condition
            if bytes[-1] == 0:

                # Remove end byte
                bytes.pop(-1)

                # Exit
                break

        # Return them
        return bytes



    def write(self, bytes = 0):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            WRITE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Write single byte to EP OUT. Tells the stick it is done writing when
            not inputed a byte.
        """

        # List
        if type(bytes) is not list:

            # Convert to list
            bytes = [bytes]

        # Write bytes to EP OUT
        for b in bytes:

            # Write
            self.EPs["OUT"].write(chr(b))



    def parse(self, bytes):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            PARSE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Parse bytes and convert payload to packet.
        """

        # Parse packet (remove EOP zero)
        self.bytes["ID"], self.bytes["RSSI"] = bytes[0], bytes[1]
        self.bytes["Payload"] = bytes[2:-1]

        # Show ID and RSSI
        print "ID: " + str(self.bytes["ID"])
        print "RSSI: " + str(self.bytes["RSSI"])

        # Create packet
        self.packet = packets.Packet(self.bytes["Payload"])

        # Parse it
        self.packet.parse()

        # Show it
        self.packet.show()



    def findError(self, bytes):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            FINDERROR
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Test bytes for CC1111 error.
        """

        # Look for possible error
        for errorType, errors in sorted(self.errors.iteritems()):

            # Match
            if bytes[-1] in errors:

                # Get error
                error = errors[bytes[-1]]

                # Show it
                print "Error [" + errorType + "]: " + error

                # Return
                return True

        # No error
        return False



    def readRegister(self, register):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            READREGISTER
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Read from radio register.
        """

        # Command
        self.write(self.commands["Register RX"])

        # Define register address
        self.write(register)

        # Read value
        value = self.read()[0]

        # Update its value
        print "Register " + str(register) + ": " + str(value)

        # Return value
        return value



    def writeRegister(self, register, value):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            WRITEREGISTER
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Write to radio register.
        """

        # Command
        self.write(self.commands["Register TX"])

        # Define register address
        self.write(register)

        # Update its value
        self.write(value)



    def tune(self, f):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            TUNE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Tune radio to given frequency in MHz.
        """

        # Info
        print "Tuning radio to: " + str(f) + " MHz"

        # Convert frequency to corresponding value (according to datasheet)
        f = int(round(f * (2 ** 16) / self.frequency))

        # Convert to set of 3 bytes
        bytes = [lib.getByte(f, x) for x in reversed(range(3))]

        # Define corresponding registers
        registers = [self.registers.index("FREQ2"),
                     self.registers.index("FREQ1"),
                     self.registers.index("FREQ0")]

        # Number of registers
        n = len(registers)

        # Update registers
        for i in range(n):

            # Write to register
            self.writeRegister(registers[i], bytes[i])

            # If mismatch
            if self.readRegister(registers[i]) != bytes[i]:

                # Raise error
                raise IOError("Register not updated correctly.")

        # Info
        print "Radio tuned."



    def listen(self, channel = 0, timeout = 1000):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            LISTEN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Listen to incoming packets on radio, using a given timeout.
        """

        # Convert timeout to bytes
        timeoutRadio = lib.pack(timeout, 4)

        # Increase timeout (1s) at EP to make sure radio is done
        timeout += 1000

        # Read from radio indefinitely
        while True:
        
            # Radio command
            self.write(self.commands["Radio RX"])

            # Give channel
            self.write(channel)

            # Give timeout as long word (32 bits)
            self.write(timeoutRadio)

            # Read response
            bytes = self.read(timeout = timeout)

            # Look for possible error
            if not self.findError(bytes):

                # Parse bytes
                self.parse(bytes)



    def sendAndListen(self, bytes, channelTX = 0, channelRX = 0,
                            repeat = 1, repeatDelay = 0,
                            retries = 2, timeout = 500):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            SENDANDLISTEN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Send packets using radio. Repeat if necessary. Following that,
            listen for incoming packets, using a given timeout. Retry the whole
            if necessary.
        """

        # Pack times
        timeoutRadio = lib.pack(timeout, 4)
        repeatDelay = lib.pack(repeatDelay, 4)

        # Adjust timeout based on number of trials and give some slack (1s) at
        # EP to make sure radio is done
        timeout *= 1 + retries
        timeout += 500

        # Radio send and receive command
        self.write(self.commands["Radio TX/RX"])

        # Give TX channel and repeat
        self.write(channelTX)
        self.write(repeat)

        # Give delay as long word (32 bits)
        self.write(repeatDelay)

        # Give RX channel
        self.write(channelRX)

        # Give timeout as long word (32 bits)
        self.write(timeoutRadio)

        # Give retry count
        self.write(retries)

        # Send bytes
        self.write(bytes)

        # Send last byte
        self.write(0)

        # Read response
        bytes = self.read(timeout = timeout)

        # Look for possible error
        if not self.findError(bytes):

            # Parse bytes
            self.parse(bytes)



    def testComms(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            TESTCOMMS
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Test communication with pump.
        """

        # Define packets
        pkts = {"Time": packets.Packet(["A7", "79", "91", "63",
                                        "70", "00", "55"]),
                "Model": packets.Packet(["A7", "79", "91", "63",
                                         "8D", "00", "C8"]),
                "Firmware": packets.Packet(["A7", "79", "91", "63",
                                            "74", "00", "0D"]),
                "Battery": packets.Packet(["A7", "79", "91", "63",
                                           "72", "00", "79"]),
                "Reservoir": packets.Packet(["A7", "79", "91", "63",
                                             "73", "00", "6F"]),
                "Status": packets.Packet(["A7", "79", "91", "63",
                                          "CE", "00", "28"])}

        # Go through them
        for name, pkt in sorted(pkts.iteritems()):

            # Info
            print "// " + name + " //"

            # Try
            try:

                # Send and listen to radio
                self.sendAndListen(pkt.bytes["Encoded"])

            # Except
            except errors.InvalidPacket:

                # Info
                print "Corrupted packet."



def main():

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        MAIN
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Instanciate a stick
    stick = Stick()

    # Find it
    stick.find()

    # Configure it
    stick.configure()

    # Listen to radio
    #stick.listen()

    # Test communications
    stick.testComms()



# Run this when script is called from terminal
if __name__ == "__main__":
    main()