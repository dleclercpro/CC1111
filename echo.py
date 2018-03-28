#! /usr/bin/python
# -*- coding: utf-8 -*-

# LIBRARIES



# USER LIBRARIES
import lib
import packets



# FUNCTIONS
def testPackets():

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        TESTPACKETS
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Define test packets
    tests = {
        "Power down": [packets.DecodedPacket(["A7", "79", "91", "63", "5D", "00", "C6"]),
            packets.EncodedPacket([169, 101, 153, 103, 25, 163, 148, 213, 85, 178, 101])],
        "Power up": [packets.DecodedPacket(["A7", "79", "91", "63", "5D", "02", "01", "0A",
                                     "00", "00", "00", "00", "00", "00", "00", "00",
                                     "00", "00", "00", "00", "00", "00", "00", "00",
                                     "00", "00", "00", "00", "00", "00", "00", "00",
                                     "00", "00", "00", "00", "00", "00", "00", "00",
                                     "00", "00", "00", "00", "00", "00", "00", "00",
                                     "00", "00", "00", "00", "00", "00", "00", "00",
                                     "00", "00", "00", "00", "00", "00", "00", "00",
                                     "00", "00", "00", "00", "00", "00", "99"]),
            packets.EncodedPacket([169, 101, 153, 103, 25, 163, 148, 213,
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
                            85, 101, 149])],
        "Time": [packets.DecodedPacket(["A7", "79", "91", "63", "70", "00", "55"]),
            packets.EncodedPacket([169, 101, 153, 103, 25, 163, 89, 85, 85, 150, 85])],
        "Model": [packets.DecodedPacket(["A7", "79", "91", "63", "8D", "00", "C8"]),
            packets.EncodedPacket([169, 101, 153, 103, 25, 163, 104, 213, 85, 177, 165])],
        "Firmware": [packets.DecodedPacket(["A7", "79", "91", "63", "74", "00", "0D"]),
            packets.EncodedPacket([169, 101, 153, 103, 25, 163, 91, 69, 85, 84, 213])],
        "Battery": [packets.DecodedPacket(["A7", "79", "91", "63", "72", "00", "79"]),
            packets.EncodedPacket([169, 101, 153, 103, 25, 163, 91, 37, 85, 89, 149])],
        "Reservoir": [packets.DecodedPacket(["A7", "79", "91", "63", "73", "00", "6F"]),
            packets.EncodedPacket([169, 101, 153, 103, 25, 163, 90, 53, 85, 153, 197])],
        "Status": [packets.DecodedPacket(["A7", "79", "91", "63", "CE", "00", "28"]),
            packets.EncodedPacket([169, 101, 153, 103, 25, 163, 176, 229, 85, 201, 165])],
        "Button ?": [packets.DecodedPacket(["A7", "79", "91", "63", "5B", "00", "B2"]),
            packets.EncodedPacket([169, 101, 153, 103, 25, 163, 148, 181, 85, 47, 37])],
        "Button EASY": [packets.DecodedPacket(["A7", "79", "91", "63", "5B", "01", "00", "00",
                                        "00", "00", "00", "00", "00", "00", "00", "00",
                                        "00", "00", "00", "00", "00", "00", "00", "00",
                                        "00", "00", "00", "00", "00", "00", "00", "00",
                                        "00", "00", "00", "00", "00", "00", "00", "00",
                                        "00", "00", "00", "00", "00", "00", "00", "00",
                                        "00", "00", "00", "00", "00", "00", "00", "00",
                                        "00", "00", "00", "00", "00", "00", "00", "00",
                                        "00", "00", "00", "00", "00", "00", "3D"]),
            packets.EncodedPacket([169, 101, 153, 103, 25, 163, 148, 181,
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
                            85, 140, 213])],
    }

    # Loop through tests
    for name, pkts in sorted(tests.iteritems()):

        # Give test name
        print "-- " + name + " --"

        # Encode packet
        pkts[0].encode()

        # Test encoding
        print "Encoding: " + str(pkts[0].bytes["Encoded"] ==
            pkts[1].bytes["Encoded"])

        # Decode packet
        pkts[1].decode()

        # Test decoding
        print "Decoding: " + str(pkts[1].bytes["Decoded"]["Hex"] ==
            pkts[0].bytes["Decoded"]["Hex"])

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
        print "{" + str(i) + "}: " + lib.translate(bytes)



def test(stick):

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