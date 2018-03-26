#! /usr/bin/python
# -*- coding: utf-8 -*-

# LIBRARIES



# USER LIBRARIES
import lib



# FUNCTIONS
def testPackets():

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        TESTPACKETS
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Define tests
    tests = {
        "Power down": ["A7 79 91 63 5D 00 C6",
            [169, 101, 153, 103, 25, 163, 148, 213, 85, 178, 101]],
        "Power up": ["A7 79 91 63 5D 02 01 0A " +
                     "00 00 00 00 00 00 00 00 " +
                     "00 00 00 00 00 00 00 00 " +
                     "00 00 00 00 00 00 00 00 " +
                     "00 00 00 00 00 00 00 00 " +
                     "00 00 00 00 00 00 00 00 " +
                     "00 00 00 00 00 00 00 00 " +
                     "00 00 00 00 00 00 00 00 " +
                     "00 00 00 00 00 00 99",
            [169, 101, 153, 103, 25, 163, 148, 213,
             114, 87, 21, 106, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 101, 149]
            ],
        "Time": ["A7 79 91 63 70 00 55",
            [169, 101, 153, 103, 25, 163, 89, 85, 85, 150, 85]],
        "Model": ["A7 79 91 63 8D 00 C8",
            [169, 101, 153, 103, 25, 163, 104, 213, 85, 177, 165]],
        "Firmware": ["A7 79 91 63 74 00 0D",
            [169, 101, 153, 103, 25, 163, 91, 69, 85, 84, 213]],
        "Battery": ["A7 79 91 63 72 00 79",
            [169, 101, 153, 103, 25, 163, 91, 37, 85, 89, 149]],
        "Reservoir": ["A7 79 91 63 73 00 6F",
            [169, 101, 153, 103, 25, 163, 90, 53, 85, 153, 197]],
        "Status": ["A7 79 91 63 CE 00 28",
            [169, 101, 153, 103, 25, 163, 176, 229, 85, 201, 165]],
        "Button announcement?": ["A7 79 91 63 5B 00 B2",
            [169, 101, 153, 103, 25, 163, 148, 181, 85, 47, 37]],
        "Button EASY": ["A7 79 91 63 5B 01 00 00 " +
                        "00 00 00 00 00 00 00 00 " +
                        "00 00 00 00 00 00 00 00 " +
                        "00 00 00 00 00 00 00 00 " +
                        "00 00 00 00 00 00 00 00 " +
                        "00 00 00 00 00 00 00 00 " +
                        "00 00 00 00 00 00 00 00 " +
                        "00 00 00 00 00 00 00 00 " +
                        "00 00 00 00 00 00 3D",
            [169, 101, 153, 103, 25, 163, 148, 181,
             113, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 85, 85, 85, 85, 85, 85, 85,
             85, 140, 213]],
    }

    # Loop through tests
    for test, values in sorted(tests.iteritems()):

        # Give test name
        print "-- " + test + " --"

        # Test encoding
        print "Encoding: " + str(lib.encodePacket(values[0]) == values[1])

        # Test decoding
        print "Decoding: " + str(lib.decodePacket(values[1]) == values[0])

        # Breathe
        print



def register(stick):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        REGISTER
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Read register
    stick.write(2)
    stick.write(0)

    # Read bytes
    print "Reading: " + str(stick.read())

    # Write to register
    stick.write(3)
    stick.write(0)
    stick.write(100)

    # Read register
    stick.write(2)
    stick.write(0)

    # Read bytes
    print "Reading: " + str(stick.read())



def commands(stick):

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
        stick.write(i)

        # Read bytes
        bytes = stick.read()

        # Convert to string and print
        print "{" + str(i) + "}: " + lib.decodeBytes(bytes)



def test(EPs):

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        TEST
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Test command
    stick.write(99)

    # Write long word (32 bits) from MSB to LSB
    for t in [255, 155, 60, 75]:

        # Compute bits
        stick.write(t)

    # Initialize them
    bytes = []

    # Read bytes
    for i in range(4):

        # Append current byte
        bytes.extend(stick.read())

    # Show them
    print "Read: " + str(bytes)



def main():

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        MAIN
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Instanciate a stick
    #stick = Stick()

    # Find it
    #stick.find()

    # Configure it
    #stick.configure()

    # Listen to radio
    #stick.listen()

    # Test register
    #register(stick)

    # Test commands
    #commands(stick)

    # Test functions
    #test(stick)

    # Test packet encoding/decoding
    testPackets()



# Run this when script is called from terminal
if __name__ == "__main__":
    main()