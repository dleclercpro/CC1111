#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Title:    lib

    Author:   David Leclerc

    Version:  0.1

    Date:     27.03.2018

    License:  GNU General Public License, Version 3
              (http://www.gnu.org/licenses/gpl.html)

    Overview: This is a script that contains user-defined functions that come in
              handy when dealing with the PyUSB library, bits, and bytes.

    Notes:    ...

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

# LIBRARIES
import math
import usb



# USER LIBRARIES
import errors



# FUNCTIONS
def NatToBytes(x, n = None, order = ">"):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        NATTOBYTES
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        This converts a natural number to its representation in bytes, given a
        minimal number of bytes to be returned in a certain order.
    """

    # Only natural numbers
    if x < 0 or int(x) != x:

        # Raise error
        raise ArithmeticError("Only natural numbers allowed.")

    # Compute minimum number of bytes required (no byte would not make sense)
    N = 1

    # Loop until number is covered
    while x >= 8 ** N:

        # Increase it
        N += 1

    # If number of wanted bytes not given
    if n is None:

        # Assign it minimum required
        n = N

    # If it is too small though
    elif n < N:

        # Raise error
        raise ArithmeticError("Minimum number of bytes required to represent " +
                              str(x) + ": " + str(N))

    # Show number in bytes
    #print "Number: " + str(x) + " (" + str(bin(x)) + ")"

    # Show its length
    #print "Number of bytes: " + str(n)

    # Initialize bytes and their string representation
    bytes = []
    bytes_ = []

    # Build bytes
    for i in range(n):

        # Compute ith byte
        bytes.insert(0, (x & (0xFF << (8 * i))) >> (8 * i))

    # Sort them according to given order
    # From MSB to LSB
    if order == ">":

        # Already ordered
        pass

    # From LSB to MSB
    elif order == "<":

        # Order
        bytes.reverse()

    # Otherwise
    else:

        # Raise error
        raise NotImplementedError("Unknown byte order.")

    # Build their string representation
    for b in bytes:

        # Convert byte to string
        byte = bin(b)[2:]

        # Fill with zeros
        while len(byte) != 8:

            # Add zero upfront
            byte = "0" + byte

        # Append byte
        bytes_.append(byte)

    # Show them
    #print bytes_

    # Return them
    return bytes



def decodeBytes(bytes):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        DECODEBYTES
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        This converts and returns the bytes received on the IN EP of the CC1111
        USB stick.
    """

    # Decode bytes
    return "".join([chr(x) for x in bytes])



def formatPacket(packet, n = 2):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        FORMATPACKET
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        This formats a packet (of type string) by regrouping characters in
        groups of n, which are then returned as a whole string.
    """

    # Make sure there are no spaces
    packet = packet.replace(" ", "")

    # Compute number of character groups of n length
    N = int(math.ceil(len(packet) / float(n)))

    # Return said groups with spaces in between
    return " ".join([packet[(n * i):(n * (i + 1))] for i in range(0, N)])



def decodePacket(bytes):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        DECODEPACKET
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        This decodes a raw packet received by CC1111 USB stick. It converts
        received bytes to a long bit-string, then uses a given table and decodes
        every 6-bit word in said string, starting from the beginning.
    """

    # Define conversion table
    TABLE = ["010101", "110001", "110010", "100011", # 0 1 2 3
             "110100", "100101", "100110", "010110", # 4 5 6 7
             "011010", "011001", "101010", "001011", # 8 9 A B
             "101100", "001101", "001110", "011100"] # C D E F

    # Show bytes
    #print "Decoding: " + str(bytes)

    # Convert bytes to long bit-string
    bits = "".join(["{:08b}".format(x) for x in bytes])

    # Show it
    #print "Bits: " + bits

    # Initialize packet
    packet = []

    # Scan bits
    while bits:

        # Get 6-bits word and shorten rest of bits
        word, bits = bits[:6], bits[6:]

        # Show word
        #print word

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
            packet.append(word)

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

    # Stringify packet
    packet = "".join(packet)

    # Format it
    packet = formatPacket(packet)

    # Show packet
    #print "Decoded packet: " + packet

    # Return packet
    return packet



def encodePacket(packet):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ENCODEPACKET
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        This encodes a string packet to be sent using the CC1111 USB stick. It
        uses the same encoding/decoding logic described in the decodePacket
        function, only the other way around this time.
    """

    # Define conversion table
    TABLE = ["010101", "110001", "110010", "100011", # 0 1 2 3
             "110100", "100101", "100110", "010110", # 4 5 6 7
             "011010", "011001", "101010", "001011", # 8 9 A B
             "101100", "001101", "001110", "011100"] # C D E F

    # Show packet
    #print "Encoding: " + packet

    # Remove spaces
    packet = packet.replace(" ", "")

    # Initialize bits
    bits = ""

    # Convert every character to its series of bits
    for p in packet:

        # Use table to convert it
        p = TABLE[int(p, 16)]

        # Add new bits
        bits += p

    # Add mysterious last bits
    bits += "0101"

    # Get number of bits
    n = len(bits)

    # If number of bits not multiple of 8, encoding fails
    if n % 8 != 0:

        # Raise error
        raise errors.InvalidPacketMissingBits(n)

    # Show bits
    #print "Bits: " + bits

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

    # Show bytes
    #print "Encoded bytes: " + str(bytes)

    # Return them
    return bytes



def getEP(configuration, direction, interface = 0, setting = 0):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        GETEP
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        This finds a matching EP on a USB device given a configuration, a
        direction, an interface and a setting input, using the PyUSB library.
    """

    # Get direction
    # IN
    if direction == "IN":

        # Reassign it
        direction = usb.util.ENDPOINT_IN

    # OUT
    elif direction == "OUT":

        # Reassign it
        direction = usb.util.ENDPOINT_OUT

    # Otherwise
    else:

        # Raise error
        raise IOError("Bad EP direction: " + direction)

    # Return EP
    return usb.util.find_descriptor(configuration[(interface, setting)],
        custom_match = lambda e:
            usb.util.endpoint_direction(e.bEndpointAddress) == direction)