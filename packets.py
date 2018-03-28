#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Title:    packets

    Author:   David Leclerc

    Version:  0.1

    Date:     27.03.2018

    License:  GNU General Public License, Version 3
              (http://www.gnu.org/licenses/gpl.html)

    Overview: This is a script that deals with the assembly, decoding and
              encoding of packets aimed at Medtronic MiniMed insulin pumps.

    Notes:    ...

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

# LIBRARIES
import math



# USER LIBRARIES
import lib
import errors



# CONSTANTS
# Packet conversion table
TABLE = ["010101", "110001", "110010", "100011", # 0 1 2 3
         "110100", "100101", "100110", "010110", # 4 5 6 7
         "011010", "011001", "101010", "001011", # 8 9 A B
         "101100", "001101", "001110", "011100"] # C D E F



# CLASSES
class Packet(object):

    def __init__(self, bytes = None):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Initialize packet properties.
        """

        # Initialize characteristics
        self.type = "A7"
        self.serial = ["79", "91", "63"]
        self.code = None
        self.parameters = []
        self.payload = []
        self.CRC = None

        # Initialize lengths
        self.length = {"Encoded": 0,
                       "Decoded": 0}

        # Initialize various formats
        self.bytes = {"Encoded": [],
                      "Decoded": {"Str": [],
                                  "Hex": [],
                                  "Chr": []}}

        # If bytes given
        if bytes is not None:

            # If given as list
            if type(bytes) == list:

                # If encoded
                if type(bytes[0]) == int:

                    # Store bytes
                    self.bytes["Encoded"] = bytes

                    # Decode them
                    self.decode()

                # If decoded (only hex format)
                elif type(bytes[0]) == str:

                    # Store bytes
                    self.bytes["Decoded"]["Hex"] = bytes

                    # Format them
                    self.format()

                    # Encode them
                    self.encode()

                # Otherwise
                else:

                    # Bad input
                    raise TypeError("Bad packet format: could not decide if " +
                                    "given encoded or decoded.")

            # Otherwise
            else:

                # Bad input
                raise TypeError("Bad packet type given as input: has to be a " +
                                "list.")



    def measure(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            MEASURE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Measure packet length.
        """

        # Measure lengths
        self.length["Encoded"] = len(self.bytes["Encoded"])
        self.length["Decoded"] = len(self.bytes["Decoded"]["Hex"])



    def format(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            FORMAT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Convert decoded packet to various formats.
        """

        # Dehexify
        self.dehexify()

        # Charify
        self.charify()



    def dehexify(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DEHEXIFY
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Interpret decoded bytes in string format as hexadecimal values and
            store them.
        """

        # Convert string
        self.bytes["Decoded"]["Int"] = lib.dehexify(
            self.bytes["Decoded"]["Hex"])



    def charify(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            CHARIFY
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Convert decoded bytes in string format to their ASCII values and
            store them.
        """

        # Convert string
        self.bytes["Decoded"]["Chr"] = lib.charify(
            self.bytes["Decoded"]["Int"])



    def showEncoded(self, n = 8):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            SHOWENCODED
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Show encoded bytes.
        """

        # Compute number of exceeding bytes
        N = self.length["Encoded"] % n

        # Define number of rows to be printed 
        R = self.length["Encoded"] / n + int(N != 0)

        # Info
        print "Encoded bytes:"

        # Print formatted response
        for r in range(R):

            # Define range
            a, b = r * n, (r + 1) * n

            # Define row
            row = str(self.bytes["Encoded"][a:b])

            # Show response
            print row

        # Breathe
        print



    def showDecoded(self, n = 8):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            SHOWDECODED
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Show decoded bytes in all formats.
        """

        # Compute number of exceeding bytes
        N = self.length["Decoded"] % n

        # Define number of rows to be printed 
        R = self.length["Decoded"] / n + int(N != 0)

        # Format bytes
        self.format()

        # Info
        print "Decoded bytes:"

        # Print formatted response
        for r in range(R):

            # Define range
            a, b = r * n, (r + 1) * n

            # Define row in all formats
            rowHex = " ".join(self.bytes["Decoded"]["Hex"][a:b])
            rowChr = "".join(self.bytes["Decoded"]["Chr"][a:b])
            rowInt = str(self.bytes["Decoded"]["Int"][a:b])

            # On last row, some extra space may be needed for some formats
            if (r == R - 1) and (N != 0):

                # Define row
                rowHex += (n - N) * 3 * " "
                rowChr += (n - N) * " "

            # Build row
            row = rowHex + 3 * " " + rowChr + 3 * " " + rowInt

            # Show response
            print row

        # Breathe
        print



    def show(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            SHOW
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Info
        print "Characteristics:"

        # Show characteristics
        print "Type: " + str(self.type)
        print "Serial: " + " ".join(self.serial)
        print "Code: " + str(self.code)
        print "Parameters: " + str(self.parameters)
        print "CRC: " + str(self.CRC)

        # Breathe
        print

        # Show encoded bytes
        self.showEncoded()        

        # Show decoded bytes
        self.showDecoded()



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            This decodes a raw packet received by the CC1111. It converts
            received bytes to a long bit-string, then uses a given table and
            decodes every 6-bit word in said string, starting from the
            beginning.
        """

        # Convert bytes to long bit-string
        bits = "".join(["{:08b}".format(x) for x in self.bytes["Encoded"]])

        # Initialize string
        string = ""

        # Scan bits
        while bits:

            # Get 6-bits word and shorten rest of bits
            word, bits = bits[:6], bits[6:]

            # End-of-packet
            if word == "000000":

                # Exit
                break

            # Try converting
            try:

                # Decode word using conversion table (as hexadecimal value)
                word = TABLE.index(word)

                # Format it
                word = hex(word)[-1].upper()

                # Store word
                string += word

            # If error
            except ValueError:

                # If bits within packet
                if bits != "":

                    # Raise error
                    raise errors.InvalidPacketUnmatchedBits(word)

                # If last bits
                else:

                    # If they do not fit
                    if word != "0101":

                        # Raise error
                        raise errors.InvalidPacketBadEnd(word)

        # Split string in groups of 2 characters
        self.bytes["Decoded"]["Hex"] = lib.split(string, 2)

        # Measure
        self.measure()

        # Generate other formats as well
        self.format()



    def encode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ENCODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            This encodes a string packet to be sent using the CC1111. It uses
            the same encoding/decoding logic described in the decode function,
            only the other way around this time.
        """

        # Initialize bits
        bits = ""

        # Convert every character to its series of bits
        for x in "".join(self.bytes["Decoded"]["Hex"]):

            # Use table to convert it into bits and add them
            bits += TABLE[int(x, 16)]

        # Add mysterious last bits
        bits += "0101"

        # Get number of bits
        n = len(bits)

        # If number of bits not multiple of 8, encoding fails
        if n % 8 != 0:

            # Raise error
            raise errors.InvalidPacketMissingBits(n)

        # Initialize bytes
        bytes = []

        # Convert bits to bytes
        while bits:

            # Get byte and shorten rest of bits
            byte, bits = bits[:8], bits[8:]

            # Convert byte from binary to decimal value
            byte = int(byte, 2)

            # Store byte
            bytes.append(byte)

        # Store encoded packet
        self.bytes["Encoded"] = bytes

        # Measure
        self.measure()



    def parse(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            PARSE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Parse packet coming in from pump.
        """

        # Get op code
        self.code = self.bytes["Decoded"]["Int"][4]

        # Get CRC
        self.CRC = self.bytes["Decoded"]["Int"][-1]

        # Compute expected CRC
        expectedCRC = lib.computeCRC8(self.bytes["Decoded"]["Int"][:-1])

        # Verify CRC
        if self.CRC != expectedCRC:

            # Raise error
            raise errors.InvalidPacketBadCRC(expectedCRC, self.CRC)

        # Get payload
        self.payload = []

        # Initialize index
        i = 5

        # Go through content
        while True:

            # Current byte
            byte = self.bytes["Decoded"]["Int"][i]

            # No zero allowed
            if byte == 0:

                # Exit
                break

            # Add byte to payload
            self.payload.append(byte)

            # Increment
            i += 1

        # Show
        print "Parsed packet information:"
        print "Code: " + str(self.code)
        print "CRC: " + str(self.CRC)
        print "Payload: " + str(self.payload)



    def assemble(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ASSEMBLE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            Assembling of packet in its string version.
        """

        # Reset decoded bytes
        self.bytes["Decoded"]["Hex"] = []

        # Add type
        self.bytes["Decoded"]["Hex"].append(self.type)

        # Add pump serial number
        self.bytes["Decoded"]["Hex"].extend(self.serial)

        # Add code
        self.bytes["Decoded"]["Hex"].append(self.code)

        # Add parameters
        self.bytes["Decoded"]["Hex"].extend(self.parameters)

        # Format them
        self.format()

        # Compute CRC
        self.CRC = lib.computeCRC8(self.bytes["Decoded"]["Int"])

        # Format it
        self.CRC = hex(self.CRC)[-2:].upper()

        # Add it
        self.bytes["Decoded"]["Hex"].append(self.CRC)

        # Format packet
        self.format()

        # Measure it
        self.measure()



def main():

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        MAIN
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Instanciate an encoded packet
    packet = Packet([169, 101, 153, 103, 25, 163, 89, 85, 85, 150, 85])

    # Show it
    packet.show()


    # Instanciate a decoded packet
    packet = Packet(["A7", "79", "91", "63", "70", "00", "55"])

    # Show it
    packet.show()


    # Instanciate an empty packet
    packet = Packet()

    # Give it characteristics
    packet.code = "5D"
    packet.parameters = "00"

    # Assemble it
    packet.assemble()

    # Show it
    packet.show()



# Run this when script is called from terminal
if __name__ == "__main__":
    main()