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

    # Initialize counter
    i = 1

    # Read bytes
    while True:

        # Read, decode, and append new bytes
        bytes += EP.read(n)

        # Update counter
        i += 1

        # Exit condition
        if bytes[-1] == 0:

            # Remove end byte
            bytes.pop(-1)

            # Exit
            break

    # Return them
    return bytes



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

    # Test bytes
    testBytes = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    
    # Test data EPs
    for i in testBytes:

        # Write byte
        EPs["OUT"].write(i)

        # Read bytes
        bytes = read(EPs["IN"])

        # Convert to string and print
        print i + ": " + decode(bytes)



# Run this when script is called from terminal
if __name__ == "__main__":
    main()