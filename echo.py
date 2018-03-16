#! /usr/bin/python
# -*- coding: utf-8 -*-

# LIBRARIES
import usb.core
import usb.util
import time



# FUNCTIONS
def getEP(configuration, direction, interface, setting = 0):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        GETEP
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

    # Get EP
    EP = usb.util.find_descriptor(configuration[(interface, setting)],
        custom_match = lambda e: 
            usb.util.endpoint_direction(e.bEndpointAddress) == direction)

    # Return it
    return EP



def toBytes(x, n = None, sort = ">"):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        TOBYTES
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

    # Print number in bytes
    print "Number: " + str(bin(x))
    print "Number of bytes: " + str(n)

    # Initialize bytes
    bytes = []

    # Build bytes
    for i in range(n):

        # Compute ith byte
        bytes.insert(0, (x & (0xFF << (8 * i))) >> (8 * i))

    # Sort them
    # From MSB to LSB
    if sort == ">":

        # Already sorted
        pass

    # From LSB to MSB
    elif sort == "<":

        # Sort
        bytes.reverse()

    # Otherwise
    else:

        # Raise error
        raise NotImplementedError("Unknown sorting pattern.")

    # Show them
    print [bin(i) for i in bytes]

    # Return them
    return bytes



def decode(bytes):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        DECODE
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Decode bytes
    return "".join([chr(x) for x in bytes])



def decode4x6(bytes):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        DECODE4X6
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Define conversion table
    TABLE = ["010101", "110001", "110010", "100011", "110100", "100101",
             "100110", "010110", "011010", "011001", "101010", "001011",
             "101100", "001101", "001110", "011100"]

    # Initialize packet
    packet = []

    # Convert bytes to bits
    bits = ["{:08b}".format(x) for x in bytes]

    # Join them all together
    bits = "".join(bits)

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

            # Convert word using conversion table
            word = hex(TABLE.index(word))[-1].upper()

            # Store word
            packet.append(word)

        # If error
        except ValueError:

            # Skip
            print "Error while converting bytes."

    # Stringify packet
    packet = "".join(packet)

    # Return packet
    return packet



def encode4x6(packet):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ENCODE4X6
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Define conversion table
    TABLE = ["010101", "110001", "110010", "100011", "110100", "100101",
             "100110", "010110", "011010", "011001", "101010", "001011",
             "101100", "001101", "001110", "011100"]

    # Initialize bits and bytes
    bits = bytes = []

    # Scan packet
    for p in packet:

        # Try converting
        try:

            # Build new bits
            new = [TABLE[p >> 4], TABLE[p & 15]]

            # Convert them
            bits.extend(["{:06b}".format(x) for x in new])

        # If error
        except ValueError:

            # Skip
            print "Error while converting packet."

    # Join them all together and pad them with extra zeros
    bits = "".join(bits) + 12 * "0"

    # Retrieve bytes
    while len(bits) >= 8:

        # Get byte and shorten rest of bits
        byte, bits = bits[:8], bits[8:]

        # Convert byte to decimal value
        byte = int(byte, 2)

        # Store byte
        bytes.append(byte)

    # Return bytes
    return bytes

    # # Try converting
    # try:

    #     # Convert packet to bits
    #     bits = [TABLE[int(x, 16)] for x in packet]

    # # If error
    # except ValueError:

    #     # Skip
    #     print "Error while converting packet."

    # # Join them all together
    # bits = "".join(bits)

    # # Scan bits
    # while bits:

    #     # Get byte and shorten bits
    #     byte, bits = bits[:8], bits[8:]

    #     # Convert byte to decimal value
    #     byte = int(byte, 2)

    #     # Store byte
    #     bytes.append(byte)

    # # Return bytes
    # return bytes



def read(EP):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        READ
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Initialize bytes
    bytes = []

    # Number of bytes to read on EP
    n = 64

    # Read bytes
    while True:

        # Read, decode, and append new bytes
        bytes += EP.read(n, timeout = 1500)

        # Exit condition
        if bytes[-1] == 0:

            # Remove end byte
            bytes.pop(-1)

            # Exit
            break

    # Return them
    return bytes



def radio(EPs):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        RADIO
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Test data EPs
    while True:
    
        # Write byte
        EPs["OUT"].write(chr(50))

        # Give channel
        EPs["OUT"].write(chr(0))

        # Convert timeout to long word (32 bits)
        bytes = toBytes(1000, 4)

        # Give timeout
        for b in bytes:

            # Compute bits
            EPs["OUT"].write(chr(b))

        # Read them
        bytes = read(EPs["IN"])

        # If timeout error
        if bytes[-1] == 0xAA:

            # Convert to string and print
            print "Timeout."

        # If no data error
        elif bytes[-1] == 0xBB:

            # Convert to string and print
            print "No data."

        # Otherwise
        else:

            # Convert to string and print
            print bytes
            print "".join(decode4x6(bytes[2:]))



def register(EPs):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        REGISTER
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Read register
    EPs["OUT"].write(chr(2))
    EPs["OUT"].write(chr(0))

    # Read bytes
    print "Reading: " + str(read(EPs["IN"]))

    # Write to register
    EPs["OUT"].write(chr(3))
    EPs["OUT"].write(chr(0))
    EPs["OUT"].write(chr(100))

    # Read register
    EPs["OUT"].write(chr(2))
    EPs["OUT"].write(chr(0))

    # Read bytes
    print "Reading: " + str(read(EPs["IN"]))



def commands(EPs):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        COMMANDS
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Test commands
    commands = [0, 1]
    
    # Do commands
    for i in commands:

        # Write byte
        EPs["OUT"].write(chr(i))

        # Read bytes
        bytes = read(EPs["IN"])

        # Convert to string and print
        print "{" + str(i) + "}: " + decode(bytes)



def test4by6():

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        TEST4BY6
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Test encoding 4x6
    print encode4x6("A77991635D00C6")

    # Test decoding 4x6
    print decode4x6([169, 101, 153, 103, 25, 163, 148, 213, 85, 178, 101])



def test(EPs):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        TEST
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Test command
    EPs["OUT"].write(chr(99))

    # Write long word (32 bits)
    EPs["OUT"].write(chr(4))
    EPs["OUT"].write(chr(5))
    EPs["OUT"].write(chr(6))
    EPs["OUT"].write(chr(7))

    # Read bytes
    print "Reading: " + str(read(EPs["IN"]))
    print "Reading: " + str(read(EPs["IN"]))
    print "Reading: " + str(read(EPs["IN"]))
    print "Reading: " + str(read(EPs["IN"]))



def main():

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        MAIN
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Find stick
    stick = usb.core.find(idVendor = 0x0451, idProduct = 0x16A7)

    # No stick found
    if stick is None:

        # Raise error
        raise IOError("No stick found.")

    # Otherwise
    #else:

        # Show stick
        #print stick

    # Set configuration
    stick.set_configuration()

    # Get configuration
    config = stick.get_active_configuration()

    # Get EPs
    EPs = {"IN": getEP(config, "IN", 0),
           "OUT": getEP(config, "OUT", 0)}

    # Test radio
    #radio(EPs)

    # Test register
    #register(EPs)

    # Test commands
    #commands(EPs)

    # Test functions
    test(EPs)

    # Test bytes function
    #toBytes(1000, 3)



# Run this when script is called from terminal
if __name__ == "__main__":
    main()