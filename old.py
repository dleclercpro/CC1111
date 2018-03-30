#! /usr/bin/python
# -*- coding: utf-8 -*-

# LIBRARIES



# CONSTANTS
TABLE = [0b010101, 0b110001, 0b110010, 0b100011,
         0b110100, 0b100101, 0b100110, 0b010110,
         0b011010, 0b011001, 0b101010, 0b001011,
         0b101100, 0b001101, 0b001110, 0b011100]



# FUNCTIONS
def oldEncodePacket(string):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        OLDENCODEPACKET
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

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



def test(errors):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        TEST
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Try
    try:

        # Raise error
        raise NotImplementedError("Test")

    # Except
    except Exception as e:

        # Errors not tolerated
        if errors:

            # Stop
            raise



def test1(a = 0, b = 1, c = 2):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        TEST1
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Return values
    return



def test2(*args):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        TEST2
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Do test 1
    return test1(*args)



def main():

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        MAIN
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Test 1
    #test(False)

    # Test 2
    print test2("A", "B")



# Run this when script is called from terminal
if __name__ == "__main__":
    main()