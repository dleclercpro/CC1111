#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Title:    commands

    Author:   David Leclerc

    Version:  0.1

    Date:     28.03.2018

    License:  GNU General Public License, Version 3
              (http://www.gnu.org/licenses/gpl.html)

    Overview: This is a script that contains various commands to control a
    		  Medtronic MiniMed insulin pump over radio frequencies using the
    		  Texas Instruments CC1111 USB radio stick.

    Notes:    ...

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

# LIBRARIES



# USER LIBRARIES
import lib
import errors
import stick
import packets



# CLASSES
class Command(object):
	pass



class StickCommand(Command):
	pass



class PumpCommand(Command):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Instanciate a packet
        self.packet = packets.Packet()

        # Define packet properties
        self.packet.recipient = "A7"
        self.packet.serial = ["79", "91", "63"]

        # Store stick instance
        self.stick = stick



    def run(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RUN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Assemble packet
        self.packet.assemble()

        # Show packet
        self.packet.show()

        # Try command
        try:

            # Send packet and listen for pump response
    		self.stick.sendAndListen(self.packet.bytes["Encoded"])

        # Comms error
        except (errors.InvalidPacket, errors.RadioError):

            # Info
            print "Corrupted packet."



class ReadPumpTime(PumpCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(self.__class__, self).__init__(stick)

        # Define packet properties
        self.packet.code = "70"
        self.packet.payload = ["00"]



class ReadPumpModel(PumpCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(self.__class__, self).__init__(stick)

        # Define packet properties
        self.packet.code = "8D"
        self.packet.payload = ["00"]



class ReadPumpFirmware(PumpCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(self.__class__, self).__init__(stick)

        # Define packet properties
        self.packet.code = "74"
        self.packet.payload = ["00"]



class ReadPumpBattery(PumpCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(self.__class__, self).__init__(stick)

        # Define packet properties
        self.packet.code = "72"
        self.packet.payload = ["00"]



class ReadPumpReservoir(PumpCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(self.__class__, self).__init__(stick)

        # Define packet properties
        self.packet.code = "73"
        self.packet.payload = ["00"]



class ReadPumpStatus(PumpCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(self.__class__, self).__init__(stick)

        # Define packet properties
        self.packet.code = "CE"
        self.packet.payload = ["00"]



def main():

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        MAIN
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Instanciate a stick
    _stick = stick.Stick()

    # Find it
    _stick.find()

    # Configure it
    _stick.configure()

    # Define commands
    cmds = {"Time": ReadPumpTime(_stick),
    		"Model": ReadPumpModel(_stick),
    		"Firmware": ReadPumpFirmware(_stick),
    		"Battery": ReadPumpBattery(_stick),
    		"Reservoir": ReadPumpReservoir(_stick),
    		"Status": ReadPumpStatus(_stick)}

    # Go through them
    for name, cmd in sorted(cmds.iteritems()):

        # Info
        print "// " + name + " //"

        # Send and listen to radio
        cmd.run()



# Run this when script is called from terminal
if __name__ == "__main__":
    main()