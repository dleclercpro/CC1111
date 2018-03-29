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
import commands
import stick



def main():

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        MAIN
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Instanciate a stick
    _stick = stick.Stick()

    # Start it
    _stick.start()

    # Define pump commands
    cmds = {"Time": commands.ReadPumpTime(_stick),
            "Model": commands.ReadPumpModel(_stick),
            "Firmware": commands.ReadPumpFirmware(_stick),
            "Battery": commands.ReadPumpBattery(_stick),
            "Reservoir": commands.ReadPumpReservoir(_stick),
            "Status": commands.ReadPumpStatus(_stick)}

    # Go through them
    for name, cmd in sorted(cmds.iteritems()):

        # Info
        print "// " + name + " //"

        # Send and listen to radio
        cmd.run()



# Run this when script is called from terminal
if __name__ == "__main__":
    main()