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

    # Tune radio
    #_stick.tune(916.690)

    # Define pump commands
    cmds = {#"Time": commands.ReadPumpTime(_stick),
            #"Model": commands.ReadPumpModel(_stick),
            #"Firmware": commands.ReadPumpFirmware(_stick),
            #"Battery": commands.ReadPumpBattery(_stick),
            #"Reservoir": commands.ReadPumpReservoir(_stick),
            #"Status": commands.ReadPumpStatus(_stick),
            #"Settings": commands.ReadPumpSettings(_stick),
            #"BG Units": commands.ReadPumpBGUnits(_stick),
            #"Carb Units": commands.ReadPumpCarbUnits(_stick),
            #"BG Targets": commands.ReadPumpBGTargets(_stick),
            #"ISF": commands.ReadPumpISF(_stick),
            #"CSF": commands.ReadPumpCSF(_stick),
            #"Basal Profile Standard": commands.ReadPumpBasalProfileStandard(_stick),
            #"Basal Profile A": commands.ReadPumpBasalProfileA(_stick),
            #"Basal Profile B": commands.ReadPumpBasalProfileB(_stick),
            #"Daily Totals": commands.ReadPumpDailyTotals(_stick),
            "History Page": commands.ReadPumpHistoryPage(_stick)}

    # Go through them
    for name, cmd in sorted(cmds.iteritems()):

        # Info
        print "// " + name + " //"

        # Send and listen to radio
        cmd.run()



# Run this when script is called from terminal
if __name__ == "__main__":
    main()