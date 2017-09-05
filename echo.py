#! /usr/bin/python
# -*- coding: utf-8 -*-

# LIBRARIES
import usb.core
import usb.util



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
        raise ValueError("No stick found.")

    # Otherwise
    else:

        # Show stick
        print stick
        print

    # Set configuration
    stick.set_configuration()

    # Get configuration
    config = stick.get_active_configuration()

    # Show it
    print config
    print

    # Get EPs
    EPs = {"Notification": getEP(config, "IN", 0),
           "IN": getEP(config, "IN", 1),
           "OUT": getEP(config, "OUT", 1)}

    # Show it
    print EPs
    print

    # Write to EP IN
    print EPs["OUT"].write('Hello');



# Run this when script is called from terminal
if __name__ == "__main__":
    main()