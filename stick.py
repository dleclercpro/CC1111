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

# NOTES
# Packet example: power down
#  A7: RF type (pump comms)
#  79 91 63: pump serial number
#  5D: op code
#  00: parameters
#  C6: CRC



# LIBRARIES
import usb



# USER LIBRARIES
import lib



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
        self.cfg = None

        # Initialize endpoints
        self.EPs = {"EP0": None,
                    "OUT": None,
                    "IN": None}

        # Define IDs
        self.IDs = {"Vendor": 0x0451,
                    "Product": 0x16A7}

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
        self.link = usb.core.find(idVendor = self.IDs["Vendor"],
                                  idProduct = self.IDs["Product"])

        # No stick found
        if self.link is None:

            # Raise error
            raise IOError("No stick found. Are you sure it's plugged in?")

        # Otherwise
        else:

            # Show stick
            print stick



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
        self.cfg = self.link.get_active_configuration()

        # Get EPs
        self.EPs["OUT"] = lib.getEP(self.cfg, "OUT")
        self.EPs["IN"] = lib.getEP(self.cfg, "IN")



    def read(n = 64, timeout = 1000):

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



    def write(byte = 0):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            WRITE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Write single byte to EP OUT. Tells the stick it is done writing when
            not inputed a byte.
        """

        # Write byte to EP
        self.EPs["OUT"].write(chr(byte))



    def listen(timeout = 1000):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            LISTEN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Listen to incoming packets on radio, using a given timeout.
        """

        # Convert timeout to bytes
        timeoutRadio = lib.natToBytes(timeout, 4)

        # Increase timeout (1s) at EP to make sure radio is done
        timeout += 1000

        # Read from radio indefinitely
        while True:
        
            # Radio command
            self.write(50)

            # Give channel
            self.write(0)

            # Give timeout as long word (32 bits)
            for t in timeoutRadio:

                # Compute bits
                self.write(t)

            # Read response
            bytes = self.read(timeout)

            # Look for possible error
            for error, reason in self.errors["Radio"].iteritems():

                # Compare to radio errors
                if bytes[-1] == error:

                    # Show error
                    print "Error: " + reason

                    # Assign bool to error
                    error = True

                    # Exit
                    break

            # Normal case
            if not error:

                # Show bytes
                print bytes



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
    stick.listen()



# Run this when script is called from terminal
if __name__ == "__main__":
    main()