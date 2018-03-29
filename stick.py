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
import numpy as np



# USER LIBRARIES
import lib
import errors
import packets
import commands



# CLASSES
class Stick(object):

    def __init__(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Initialize stick properties.
        """

        # Define USB IDs
        self.vendor = 0x0451
        self.product = 0x16A7

        # Initialize serial link
        self.device = None

        # Initialize configuration
        self.config = None

        # Initialize data endpoints
        self.EPs = {"OUT": None,
                    "IN": None}

        # Define frequencies (MHz)
        self.freq = {"Reference": 24.0,
                     "Regions": {"NA": {"Default": 916.660,
                                        "Range": [916.645, 916.775]},
                                 "WW": {"Default": 868.330,
                                        "Range": [868.150, 868.750]}}}

        # Define radio errors
        self.errors = {0xAA: "Timeout",
                       0xBB: "No data"}

        # Define commands
        self.commands = {"Name RX": commands.ReadStickName(self),
                         "Author RX": commands.ReadStickAuthor(self),
                         "Radio Register RX": commands.ReadStickRadioRegister(self),
                         "Radio Register TX": commands.WriteStickRadioRegister(self),
                         "Radio RX": commands.ReadStickRadio(self),
                         "Radio TX": commands.WriteStickRadio(self),
                         "Radio TX/RX": commands.WriteReadStickRadio(self),
                         "LED": commands.FlashStickLED(self)}

        # Define radio registers
        self.registers = ["SYNC1",
                          "SYNC0",
                          "PKTLEN",
                          "PKTCTRL1",
                          "PKTCTRL0",
                          "ADDR",
                          "FSCTRL1",
                          "FSCTRL0",
                          "MDMCFG4",
                          "MDMCFG3",
                          "MDMCFG2",
                          "MDMCFG1",
                          "MDMCFG0",
                          "DEVIATN",
                          "MCSM2",
                          "MCSM1",
                          "MCSM0",
                          "BSCFG",
                          "FOCCFG",
                          "FREND1",
                          "FREND0",
                          "FSCAL3",
                          "FSCAL2",
                          "FSCAL1",
                          "FSCAL0",
                          "TEST1",
                          "TEST0",
                          "PA_TABLE1",
                          "PA_TABLE0",
                          "AGCCTRL2",
                          "AGCCTRL1",
                          "AGCCTRL0",
                          "FREQ2",
                          "FREQ1",
                          "FREQ0",
                          "CHANNR"]



    def start(self, scan = False):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            START
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Starting procedure for stick.
        """

        # Find it
        self.find()

        # Configure it
        self.configure()

        # If scanning wanted
        if scan:

            # Tune radio to best frequency
            self.tune(self.scan())



    def find(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            FIND
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Find the stick on the USB bus and link it.
        """

        # Find stick
        self.device = usb.core.find(idVendor = self.vendor,
                                    idProduct = self.product)

        # No stick found
        if self.device is None:

            # Raise error
            raise IOError("No stick found. Are you sure it's plugged in?")

        # Otherwise
        else:

            # Show stick
            print "Stick found."



    def configure(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            CONFIGURE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Configure the stick and assign EPs.
        """

        # Set configuration
        self.device.set_configuration()

        # Get configuration
        self.config = self.device.get_active_configuration()

        # Get EPs
        self.EPs["OUT"] = lib.getEP(self.config, "OUT")
        self.EPs["IN"] = lib.getEP(self.config, "IN")



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
        f = int(round(f * (2 ** 16) / self.freq["Reference"]))

        # Convert to set of 3 bytes
        bytes = [lib.getByte(f, x) for x in [2, 1, 0]]

        # Update registers
        for reg, byte in zip(["FREQ2", "FREQ1", "FREQ0"], bytes):

            # Write to register
            self.commands["Radio Register TX"].run(reg, byte)

            # If mismatch
            if self.commands["Radio Register RX"].run(reg) != byte:

                # Raise error
                raise IOError("Register not updated correctly.")

        # Info
        print "Radio tuned."



    def scan(self, F1 = None, F2 = None, n = 25, sample = 5):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            SCAN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Scan the air for the best frequency to use with CC1111 in order to
            communicate with pump.
        """

        # No frequencies given
        if F1 is None and F2 is None:

            # Default region: NA
            region = "NA"

            # Assign frequencies
            [F1, F2] = self.freq["Regions"][region]["Range"]

        # Otherwise, test them
        else:

            # Go through locales
            for region, freq in self.freq["Regions"].iteritems():

                # Check for correct frequencies
                if (F1 >= min(freq["Range"]) and
                    F2 <= max(freq["Range"])):

                    # Exit
                    break

                # Reset region
                region = None

            # Bad frequencies
            if region is None:

                # Raise error
                raise errors.BadFrequencies()

        # Info
        print "Scanning for a " + region + " pump..."

        # Initialize RSSI readings
        RSSIs = {}

        # Go through frequency range
        for f in np.linspace(F1, F2, n, True):

            # Format frequency
            f = round(f, 3)

            # Initialize RSSI value
            RSSIs[f] = []

            # Adjust frequency
            self.tune(f)

            # Sample size
            for i in range(sample):

                # Try
                try:

                    # Initialize command
                    cmd = commands.ReadPumpModel(self)

                    # Run pump command and get packet
                    pkt = cmd.run()

                    # Get RSSI reading and add it
                    RSSIs[f].append(pkt.RSSI["dBm"])

                # On invalid packet or radio error
                except (errors.InvalidPacket, errors.RadioError):

                    # Add fake low RSSI reading
                    RSSIs[f].append(-99)

            # Average readings
            RSSIs[f] = np.mean(RSSIs[f])

        # Destructure RSSIs
        freq, levels = RSSIs.keys(), RSSIs.values()

        # Get indices of best frequencies
        ids = np.argwhere(levels == np.max(levels)).flatten()

        # Average best frequencies
        f = np.mean([freq[i] for i in ids])

        # Show readings
        lib.printJSON(RSSIs)

        # Info
        print "Best frequency: " + str(f)

        # Return best frequency
        return f



    def listen(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            LISTEN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Listen to incoming packets on radio.
        """

        # Read from radio indefinitely
        while True:

            # Get packet
            pkt = self.commands["Radio RX"].run(tolerate = True)

            # Show it
            pkt.show()



def main():

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        MAIN
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Instanciate a stick
    stick = Stick()

    # Start it
    stick.start(True)

    # Tune radio
    #stick.tune(916.665)

    # Listen to radio
    #stick.listen()



# Run this when script is called from terminal
if __name__ == "__main__":
    main()