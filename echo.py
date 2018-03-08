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
        bytes += EP.read(n, timeout = 2000)

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

        # Give timeout
        EPs["OUT"].write(chr(1))

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
    commands(EPs)



# Run this when script is called from terminal
if __name__ == "__main__":
    main()