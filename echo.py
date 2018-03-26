#! /usr/bin/python
# -*- coding: utf-8 -*-

# LIBRARIES
import usb.core
import usb.util
import time
import math



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
    #print "Number: " + str(x) + " (" + str(bin(x)) + ")"
    #print "Number of bytes: " + str(n)

    # Initialize bytes and their string representation
    bytes = []
    bytes_ = []

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



def decode(bytes):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        DECODE
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Decode bytes
    return "".join([chr(x) for x in bytes])



def format(packet, n = 2):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        FORMAT
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Compute number of character groups of n length
    N = int(math.ceil(len(packet) / float(n)))

    # Return said groups with spaces in between
    return " ".join([packet[(n * i):(n * (i + 1))] for i in range(0, N)])



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

    # Show bytes
    #print "Decoding: " + str(bytes)

    # Convert bytes to bits
    bits = ["{:08b}".format(x) for x in bytes]

    # Join them all together
    bits = "".join(bits)

    # Show bits
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

            # Convert word to hexadecimal value using conversion table
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
                raise NotImplementedError("Unmatched bits before EOP (" +
                                          "corrupted packet): " + word)

            # If last bits
            else:

                # If they do not fit
                if word != "0101":

                    # Raise error
                    raise NotImplementedError("Last bits do not correspond " +
                                              "to expectation (0101): " + word)

    # Stringify packet
    packet = "".join(packet)

    # Format it
    packet = format(packet)

    # Show packet
    #print "Decoded packet: " + packet

    # Return packet
    return packet



def encode4x6(packet):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ENCODE4X6
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        Encoding example: power down
          A7: RF type (pump comms)
          79 91 63: pump serial number
          5D: op code
          00: parameters
          C6: CRC
    """

    # Define conversion table
    TABLE = ["010101", "110001", "110010", "100011", "110100", "100101",
             "100110", "010110", "011010", "011001", "101010", "001011",
             "101100", "001101", "001110", "011100"]

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
        raise NotImplementedError("Impossible to encode number of bytes " +
                                  "which isn't a multiple of 8: " + str(n))

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



def oldEncode4x6(string):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        OLDENCODE4X6
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Define conversion table
    TABLE = [0b010101, 0b110001, 0b110010, 0b100011, 0b110100, 0b100101,
             0b100110, 0b010110, 0b011010, 0b011001, 0b101010, 0b001011,
             0b101100, 0b001101, 0b001110, 0b011100]

    # Initialize bits, bytes and packet
    bits = []
    bytes = []
    packet = []

    # Show input string
    print "Encoding: " + string

    # Remove spaces
    string.replace(" ", "")

    # Convert it to bytes
    while string:

        # Every two characters correspond to one hexadecimal value (or byte)
        byte, string = int(string[:2], 16), string[2:]

        # Add it to bytes
        bytes.append(byte)

    # Show bytes
    print bytes

    # Scan them
    for b in bytes:

        # Try converting
        try:

            # Build new bits
            new = [TABLE[b >> 4], TABLE[b & 15]]

            # Convert them
            bits.extend(["{:06b}".format(x) for x in new])

        # If error
        except ValueError:

            # Skip
            print "Error while encoding bytes."

    # Join them all together and pad them with extra zeros
    bits = "".join(bits) + 12 * "0"

    # Convert bytes
    while len(bits) >= 8:

        # Get byte and shorten rest of bits
        byte, bits = bits[:8], bits[8:]

        # Convert byte from binary to decimal value
        byte = int(byte, 2)

        # Store byte
        packet.append(byte)

    # Show packet
    print "Encoded packet: " + str(packet)

    # Return it
    return packet



def read(EP, timeout = 1500):

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
        bytes += EP.read(n, timeout = timeout)

        # Exit condition
        if bytes[-1] == 0:

            # Remove end byte
            bytes.pop(-1)

            # Exit
            break

    # Return them
    return bytes



def write(EP, byte):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        WRITE
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Write byte to EP
    EP.write(chr(byte))



def radio(EPs, timeout = 1000):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        RADIO
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Convert timeout to bytes
    timeout_ = toBytes(timeout, 4)

    # Increase timeout (1s) at EP to make sure radio is done
    timeout += 1000

    # Test data EPs
    while True:
    
        # Write byte
        write(EPs["OUT"], 50)

        # Give channel
        write(EPs["OUT"], 0)

        # Give timeout as long word (32 bits)
        for t in timeout_:

            # Compute bits
            write(EPs["OUT"], t)

        # Read response
        bytes = read(EPs["IN"], timeout)

        # If timeout error
        if bytes[-1] == 0xAA:

            # Show error
            print "Timeout."

        # If no data error
        elif bytes[-1] == 0xBB:

            # Show error
            print "No data."

        # Otherwise
        else:

            # Convert to string and print
            print bytes
            #print "".join(decode4x6(bytes[2:]))



def register(EPs):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        REGISTER
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Read register
    write(EPs["OUT"], 2)
    write(EPs["OUT"], 0)

    # Read bytes
    print "Reading: " + str(read(EPs["IN"]))

    # Write to register
    write(EPs["OUT"], 3)
    write(EPs["OUT"], 0)
    write(EPs["OUT"], 100)

    # Read register
    write(EPs["OUT"], 2)
    write(EPs["OUT"], 0)

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
        write(EPs["OUT"], i)

        # Read bytes
        bytes = read(EPs["IN"])

        # Convert to string and print
        print "{" + str(i) + "}: " + decode(bytes)



def test4x6():

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        TEST4X6
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Define tests
    tests = {
        "Power down": ["A7 79 91 63 5D 00 C6",
            [169, 101, 153, 103, 25, 163, 148, 213, 85, 178, 101]],
        "Model": ["A7 79 91 63 8D 00 C8",
            [169, 101, 153, 103, 25, 163, 104, 213, 85, 177, 165]],
        "Time": ["A7 79 91 63 70 00 55",
            [169, 101, 153, 103, 25, 163, 89, 85, 85, 150, 85]],
        "Firmware": ["A7 79 91 63 74 00 0D",
            [169, 101, 153, 103, 25, 163, 91, 69, 85, 84, 213]]
    }

    # Loop through tests
    for test, values in tests.iteritems():

        # Give test name
        print "-- " + test + " --"

        # Test encoding
        print "Encoding: " + str(encode4x6(values[0]) == values[1])

        # Test decoding
        print "Decoding: " + str(decode4x6(values[1]) == values[0])

        # Breathe
        print



def test(EPs):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        TEST
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Test command
    write(EPs["OUT"], 99)

    # Write long word (32 bits) from MSB to LSB
    for t in [255, 155, 60, 75]:

        # Compute bits
        write(EPs["OUT"], t)

    # Initialize them
    bytes = []

    # Read bytes
    for i in range(4):

        # Append current byte
        bytes.extend(read(EPs["IN"]))

    # Show them
    print "Read: " + str(bytes)



def init():

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        INIT
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

    # Return EPs
    return EPs



def main():

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        MAIN
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Get EPs
    #EPs = init()

    # Test radio
    #radio(EPs, 1000)

    # Test register
    #register(EPs)

    # Test commands
    #commands(EPs)

    # Test functions
    #test(EPs)

    # Test encoding
    test4x6()



# Run this when script is called from terminal
if __name__ == "__main__":
    main()