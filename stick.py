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

        # Define errors
        self.errors = {"Radio": {0xAA: "Timeout",
                                 0xBB: "No data"}}



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
        #else:

            # Show stick
            #print self.link



    def configure(self):

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



    def read(self, n = 64, timeout = 1000):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            READ
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Read from EP IN until it tells it is done transmitting data using a
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



    def write(self, byte = 0):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            WRITE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Write single byte to EP OUT. Tells the stick it is done writing when
            not inputed a byte.
        """

        # Write byte to EP
        self.EPs["OUT"].write(chr(byte))



    def readRadioRegister(self, register):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            READRADIOREGISTER
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Command
        self.write(2)

        # Define register address
        self.write(register)

        # Read value
        value = self.read()[0]

        # Update its value
        print "Register " + str(register) + ": " + str(value)

        # Return value
        return value



    def writeRadioRegister(self, register, value):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            WRITERADIOREGISTER
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Command
        self.write(3)

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

        # Define reference frequency for CC1111 (MHz)
        F = 24.0

        # Convert frequency to corresponding value (according to datasheet)
        f = int(round(f * (2 ** 16) / F))

        # Convert to set of 3 bytes
        bytes = [lib.getByte(f, x) for x in reversed(range(3))]

        # Define corresponding registers
        registers = [32, 33, 34]

        # Update registers
        for i in range(3):

            # Write to register
            self.writeRadioRegister(registers[i], bytes[i])

        # Double check registers
        for i in range(3):

            # If mismatch
            if self.readRadioRegister(registers[i]) != bytes[i]:

                # Raise error
                raise IOError("Registers not updated correctly.")

        # Info
        print "Radio tuned."



    def listen(self, timeout = 1000):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            LISTEN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Listen to incoming packets on radio, using a given timeout.
        """

        # Convert timeout to bytes
        timeoutRX = lib.pack(timeout, 4)

        # Increase timeout (1s) at EP to make sure radio is done
        timeout += 1000

        # Read from radio indefinitely
        while True:
        
            # Radio command
            self.write(4)

            # Give channel
            self.write(0)

            # Give timeout as long word (32 bits)
            for t in timeoutRX:

                # Compute bits
                self.write(t)

            # Read response
            bytes = self.read(timeout = timeout)

            # Look for possible error
            if bytes[-1] in self.errors["Radio"]:

                # Show error
                print self.errors["Radio"][bytes[-1]]

            # Otherwise
            else:

                # Show bytes
                print bytes



    def sendListen(self, bytes, timeout = 1000):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            SENDLISTEN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Listen to incoming packets on radio, using a given timeout.
        """

        # Define arguments
        command = 6
        channelTX = 0
        channelRX = 0
        timeoutRX = lib.pack(timeout, 4)
        repeatTXDelay = lib.pack(0, 4)
        repeatTX = 1
        retry = 2

        # Adjust timeout based on number of trials and give some slack (1s) at
        # EP to make sure radio is done
        timeout *= 1 + retry
        timeout += 1000

        # Radio send and receive command
        self.write(command)

        # Give TX channel and repeat
        self.write(channelTX)
        self.write(repeatTX)

        # Give delay as long word (32 bits)
        for d in repeatTXDelay:

            # Write byte
            self.write(d)

        # Give RX channel
        self.write(channelRX)

        # Give timeout as long word (32 bits)
        for t in timeoutRX:

            # Write byte
            self.write(t)

        # Give retry count
        self.write(retry)

        # Info
        #print "Sending bytes..."

        # Send bytes
        for b in bytes:

            # Write byte
            self.write(b)

        # Send last byte
        self.write(0)
        
        # Info
        #print "Bytes sent."

        # Info
        #print "Waiting for response..."

        # Read response
        bytes = self.read(timeout = timeout)
        
        # Info
        #print "Response received."

        # Look for possible error
        if bytes[-1] in self.errors["Radio"]:

            # Show error
            print self.errors["Radio"][bytes[-1]]

        # Otherwise
        else:

            # Parse packet (remove EOP zero)
            index = bytes[0]
            signal = bytes[1]
            content = bytes[2:-1]

            # Create packet
            packet = packets.Packet(content)

            # Show content
            packet.show()

            # Parse it
            packet.parse()



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

    # Tune radio
    stick.tune(916.660)

    # Listen to radio
    #stick.listen()

    # Define operation packets
    pkts = {
        "Time": packets.Packet(["A7", "79", "91", "63", "70", "00", "55"]),
        "Model": packets.Packet(["A7", "79", "91", "63", "8D", "00", "C8"]),
        "Firmware": packets.Packet(["A7", "79", "91", "63", "74", "00", "0D"]),
        "Battery": packets.Packet(["A7", "79", "91", "63", "72", "00", "79"]),
        "Reservoir": packets.Packet(["A7", "79", "91", "63", "73", "00", "6F"]),
        "Status": packets.Packet(["A7", "79", "91", "63", "CE", "00", "28"]),
    }

    # Go through them
    for name, pkt in sorted(pkts.iteritems()):

        # Info
        print "-- " + name + " --"

        # Try
        try:

            # Send and listen to radio
            stick.sendListen(pkt.bytes["Encoded"])

        # Except
        except errors.InvalidPacketUnmatchedBits:

            # Info
            print "Corrupt packet."



# Run this when script is called from terminal
if __name__ == "__main__":
    main()