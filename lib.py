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
import usb



# FUNCTIONS
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