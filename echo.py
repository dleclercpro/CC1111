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



def decode(bytes):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        DECODE
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Decode bytes
    return "".join([chr(x) for x in bytes])



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
        bytes += EP.read(n, timeout = 500)

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
    #for i in range(256):
    for i in range(1):

        # Write byte
        #EPs["OUT"].write(chr(50))
        EPs["OUT"].write(chr(2))

        # Give channel
        #EPs["OUT"].write(chr(i))
        EPs["OUT"].write(chr(0))

        # Read bytes
        bytes = read(EPs["IN"])

        # Convert to string and print
        #print "Reading [" + str(i) + "]: " + decode(bytes)
        print "Reading: " + str(bytes)



def test(EPs):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        TEST
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
    EPs["OUT"].write(chr(0xFF))

    # Read register
    EPs["OUT"].write(chr(2))
    EPs["OUT"].write(chr(0))

    # Read bytes
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
    test(EPs)

    # Test bytes
    #testBytes = ["0", "1", "3", "4", "5", "6", "7", "8", "9"]
    
    # Test data EPs
    #for i in testBytes:

        # Write byte
        #EPs["OUT"].write(i)

        # Read bytes
        #bytes = read(EPs["IN"])

        # Convert to string and print
        #print i + ": " + decode(bytes)



# Run this when script is called from terminal
if __name__ == "__main__":
    main()