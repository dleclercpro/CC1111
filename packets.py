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
import errors



# CONSTANTS
# Packet conversion table
TABLE = ["010101", "110001", "110010", "100011", # 0 1 2 3
         "110100", "100101", "100110", "010110", # 4 5 6 7
         "011010", "011001", "101010", "001011", # 8 9 A B
         "101100", "001101", "001110", "011100"] # C D E F



def format(packet, n = 2):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        FORMAT
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



def decode(bytes):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        DECODE
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        This decodes a raw packet received by CC1111 USB stick. It converts
        received bytes to a long bit-string, then uses a given table and decodes
        every 6-bit word in said string, starting from the beginning.
    """

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
    packet = format(packet)

    # Show packet
    #print "Decoded packet: " + packet

    # Return packet
    return packet



def encode(packet):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ENCODE
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        This encodes a string packet to be sent using the CC1111 USB stick. It
        uses the same encoding/decoding logic described in the decode
        function, only the other way around this time.
    """

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