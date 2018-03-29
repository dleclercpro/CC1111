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
import numpy as np
import math
import json
import usb



# FUNCTIONS
def getPolyFitMax(x, y, n, N):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        GETPOLYFITMAX
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        f(x) = a_n * x^n + a_(n - 1) * x^(n - 1) + ... + a_0
    """

    # Generate nth-order polynomial fit
    a = np.polyfit(x, y, n)

    # Build x-axis
    x = np.linspace(x[0], x[-1], N)

    # Initialize y-axis
    y = np.zeros(N)

    # Loop through the n degrees of order
    for i in range(n):

        # Compute values on y-axis
        y += a[i] * x ** (n - i)

    # Find index of max
    index = np.argmax(y)

    # Return max
    return x[index]



def getMaxMiddle(x, y, threshold):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        GETMAXMIDDLE
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Get max
    yMax = np.max(y)

    # Initialize indices
    indices = []

    # Get indices or values near absolute max within threshold
    for i in range(len(x)):

        # Fits within threshold
        if y[i] >= (yMax - threshold):

            # Add index
            indices.append(i)

    # Get average index
    index = int(round(np.mean(indices)))

    # Return corresponding max
    return x[index]



def hexify(x):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        HEXIFY
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    if type(x) is not list:
        x = [x]

    return ["{0:#04X}".format(y) for y in x]



def dehexify(x):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        DEHEXIFY
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    if type(x) is not list:
        x = [x]

    return [int(y, 16) for y in x]




def charify(x):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        CHARIFY
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    if type(x) is not list:
        x = [x]

    return ["." if (y < 32) | (y > 126) else chr(y) for y in x]



def translate(x):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        TRANSLATE
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        This converts and returns the bytes received on the IN EP of the CC1111
        USB stick.
    """

    return "".join([chr(y) for y in x])



def split(x, n):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        SPLIT
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        This splits a string in groups of n characters and stores them in an
        array.
    """

    # Compute number of hexadecimal values within string
    N = int(math.ceil(len(x) / float(n)))

    # Return splitted string
    return [x[(n * i):(n * (i + 1))] for i in range(0, N)]



def getByte(x, n):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        GETBYTE
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        This is a function that extracts the byte in position n of a integer x.
    """

    return (x >> (8 * n)) & 0xFF



def pack(x, n = None, order = ">"):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        PACK
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



def computeCRC8(bytes):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        COMPUTECRC8
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Define CRC8 lookup table
    lookupTable = [0, 155, 173, 54, 193, 90, 108, 247,
                   25, 130, 180, 47, 216, 67, 117, 238,
                   50, 169, 159, 4, 243, 104, 94, 197,
                   43, 176, 134, 29, 234, 113, 71, 220,
                   100, 255, 201, 82, 165, 62, 8, 147,
                   125, 230, 208, 75, 188, 39, 17, 138,
                   86, 205, 251, 96, 151, 12, 58, 161,
                   79, 212, 226, 121, 142, 21, 35, 184,
                   200, 83, 101, 254, 9, 146, 164, 63,
                   209, 74, 124, 231, 16, 139, 189, 38,
                   250, 97, 87, 204, 59, 160, 150, 13,
                   227, 120, 78, 213, 34, 185, 143, 20,
                   172, 55, 1, 154, 109, 246, 192, 91,
                   181, 46, 24, 131, 116, 239, 217, 66,
                   158, 5, 51, 168, 95, 196, 242, 105,
                   135, 28, 42, 177, 70, 221, 235, 112,
                   11, 144, 166, 61, 202, 81, 103, 252,
                   18, 137, 191, 36, 211, 72, 126, 229,
                   57, 162, 148, 15, 248, 99, 85, 206,
                   32, 187, 141, 22, 225, 122, 76, 215,
                   111, 244, 194, 89, 174, 53, 3, 152,
                   118, 237, 219, 64, 183, 44, 26, 129,
                   93, 198, 240, 107, 156, 7, 49, 170,
                   68, 223, 233, 114, 133, 30, 40, 179,
                   195, 88, 110, 245, 2, 153, 175, 52,
                   218, 65, 119, 236, 27, 128, 182, 45,
                   241, 106, 92, 199, 48, 171, 157, 6,
                   232, 115, 69, 222, 41, 178, 132, 31,
                   167, 60, 10, 145, 102, 253, 203, 80,
                   190, 37, 19, 136, 127, 228, 210, 73,
                   149, 14, 56, 163, 84, 207, 249, 98,
                   140, 23, 33, 186, 77, 214, 224, 123]

    # Initialize CRC
    CRC = 0

    # Look for CRC in table
    for i in range(len(bytes)):
        CRC = lookupTable[CRC ^ getByte(bytes[i], 0)]

    # Return CRC
    return CRC



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



def printJSON(x):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        PRINTJSON
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Print a dictionary using a particular JSON formatting.
    """

    print json.dumps(x, indent = 2, separators = (",", ": "), sort_keys = True)