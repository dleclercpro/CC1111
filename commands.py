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
import packets



# CLASSES
class Command(object):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Store device instance
        self.device = device

        # Initialize code
        self.code = None



class StickCommand(Command):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(StickCommand, self).__init__(device)



    def checkRadioError(self, bytes):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            CHECKRADIOERROR
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # If single error byte
        if len(bytes) == 1 and bytes[-1] in self.device.errors:

            # Raise error
            raise errors.RadioError(self.device.errors[bytes[-1]])



class ReadStickName(StickCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(StickCommand, self).__init__(device)

        # Define code
        self.code = 0



    def run(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RUN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        	Read from radio register on stick.
        """

        # Send command code
        self.device.write(self.code)

        # Get data
        self.data = "".join(lib.charify(self.device.read()))

        # Info
        print "Stick name: " + self.data

        # Return it
        return self.data



class ReadStickAuthor(StickCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(StickCommand, self).__init__(device)

        # Define code
        self.code = 1



    def run(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RUN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        	Read from radio register on stick.
        """

        # Send command code
        self.device.write(self.code)

        # Get data
        self.data = "".join(lib.charify(self.device.read()))

        # Info
        print "Stick author: " + self.data

        # Return it
        return self.data



class ReadStickRadioRegister(StickCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(StickCommand, self).__init__(device)

        # Define code
        self.code = 10

        # Initialize register
        self.register = None

        # Initialize address
        self.address = None



    def run(self, register):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RUN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Store register
        self.register = register

        # Get register address
        self.address = self.device.registers.index(register)

        # Send command code
        self.device.write(self.code)

        # Send register address
        self.device.write(self.address)

        # Get data
        self.data = self.device.read()[0]

        # Info
        print "Register " + self.register + ": " + str(self.data)

        # Return it
        return self.data



class WriteStickRadioRegister(StickCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(StickCommand, self).__init__(device)

        # Define code
        self.code = 11

        # Initialize register
        self.register = None

        # Initialize address
        self.address = None

        # Initialize value
        self.value = None



    def run(self, register, value):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RUN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Store register
        self.register = register

        # Get register address
        self.address = self.device.registers.index(register)

        # Store value
        self.value = value

        # Send command code
        self.device.write(self.code)

        # Send register address
        self.device.write(self.address)

        # Send value
        self.device.write(self.value)



class ReadStickRadio(StickCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(StickCommand, self).__init__(device)

        # Define code
        self.code = 20

        # Initialize data
        self.data = None

        # Initialize channel
        self.channel = None

        # Initialize timeout
        self.timeout = None

        # Initialize radio timeout
        self.timeoutRadio = None


    def run(self, channel = 0, timeout = 500, tolerate = False):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RUN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Store channel
        self.channel = channel

        # Store timeout (plus extra time for EP)
        self.timeout = timeout + 500

        # Store radio timeout as long word
        self.timeoutRadio = lib.pack(timeout, 4)

        # Send command code
        self.device.write(self.code)

        # Send channel
        self.device.write(self.channel)

        # Send radio timeout
        self.device.write(self.timeoutRadio)

        # Try
        try:

            # Get data
            self.data = self.device.read(timeout = self.timeout)

            # Look for possible error
            self.checkRadioError(self.data)

            # Remove EOP byte
            self.data.pop(-1)

        # If radio error
        except errors.RadioError:

            # Errors not tolerated
            if not tolerate:

                # Stop
                raise

        # Return data
        return self.data



class WriteStickRadio(StickCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(StickCommand, self).__init__(device)

        # Define code
        self.code = 21

        # Initialize data
        self.data = None

        # Initialize channel
        self.channel = None

        # Initialize repeat count
        self.repeat = None

        # Initialize delay
        self.delay = None



    def run(self, data, channel = 0, repeat = 0, delay = 0):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RUN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Store packet
        self.data = data

        # Store channel
        self.channel = channel

        # Store repeat count
        self.repeat = repeat

        # Convert delay to bytes
        self.delay = lib.pack(delay, 4)

        # Send command code
        self.device.write(self.code)

        # Send channel
        self.device.write(self.channel)

        # Send delay
        self.device.write(self.delay)

        # Send packet
        self.device.write(self.data)

        # Send last byte
        self.device.write(0)



class WriteReadStickRadio(StickCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(StickCommand, self).__init__(device)

        # Define code
        self.code = 22

        # Initialize data to send
        self.dataTX = None

        # Initialize data to receive
        self.dataRX = None

        # Initialize send channel
        self.channelTX = None

        # Initialize receive channel
        self.channelRX = None

        # Initialize repeat count
        self.repeatTX = None

        # Initialize delay between each repetition
        self.delayTX = None

        # Initialize retry count
        self.retry = None

        # Initialize timeout
        self.timeout = None

        # Initialize radio timeout
        self.timeoutRadio = None



    def run(self, dataTX, channelTX = 0, channelRX = 0, repeatTX = 1,
                  delayTX = 0, retry = 1, timeout = 500, tolerate = False):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RUN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Store data to send
        self.dataTX = dataTX

        # Store send channel
        self.channelTX = channelTX

        # Store receive channel
        self.channelRX = channelRX

        # Store repeat count
        self.repeatTX = repeatTX

        # Store delay
        self.delayTX = lib.pack(delayTX, 4)

        # Store retry count
        self.retry = retry

        # Store timeout
        self.timeout = (1 + retry) * timeout + 500

        # Store radio timeout as long word
        self.timeoutRadio = lib.pack(timeout, 4)

        # Send command code
        self.device.write(self.code)

        # Send channel TX
        self.device.write(self.channelTX)

        # Send repeat count
        self.device.write(self.repeatTX)

        # Send delay
        self.device.write(self.delayTX)

        # Send channel RX
        self.device.write(self.channelRX)

        # Send radio timeout
        self.device.write(self.timeoutRadio)

        # Send retry count
        self.device.write(self.retry)

        # Send packet
        self.device.write(self.dataTX)

        # Send last byte
        self.device.write(0)

        # Try
        try:

            # Get data
            self.dataRX = self.device.read(timeout = self.timeout)

            # Look for possible error
            self.checkRadioError(self.dataRX)

            # Remove EOP byte
            self.dataRX.pop(-1)

        # If radio error
        except errors.RadioError:

            # Errors not tolerated
            if not tolerate:

                # Stop
                raise

        # Return data
        return self.dataRX



class FlashStickLED(StickCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(StickCommand, self).__init__(device)

        # Define code
        self.code = 30



    def run(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RUN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Send command code
        self.device.write(self.code)



class PumpCommand(Command):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(PumpCommand, self).__init__(device)

        # Initialize packets
        self.packetTX = None
        self.packetRX = None



    def run(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RUN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Generate packet to send to pump
        self.packetTX = packets.ToPumpPacket(self.code, self.payload)

        # Instanciate command
        cmd = WriteReadStickRadio(self.device)

        # Send encoded packet, listen for pump response and get data
        data = cmd.run(self.packetTX.bytes["Encoded"])

        # Parse data into packet and store it
        self.packetRX = packets.FromPumpPacket(data)

        # Show it
        self.packetRX.show()

        # Return it
        return self.packetRX



class PumpPreCommand(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(PumpPreCommand, self).__init__(device)



    def run(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RUN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Generate packet to send to pump
        self.packetTX = packets.ToPumpPacket(self.code, self.payload)

        # Instanciate command
        cmd = WriteStickRadio(self.device)

        # Send encoded packet
        cmd.run(self.packetTX.bytes["Encoded"])



class PumpBigCommand(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(PumpBigCommand, self).__init__(device)

        # Initialize commands to run one after the other
        self.commands = []



    def run(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RUN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # ...



class ReadPumpTime(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpTime, self).__init__(device)

        # Define code
        self.code = "70"

        # Define payload
        self.payload = ["00"]



class ReadPumpModel(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpModel, self).__init__(device)

        # Define code
        self.code = "8D"

        # Define payload
        self.payload = ["00"]



class ReadPumpFirmware(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpFirmware, self).__init__(device)

        # Define code
        self.code = "74"

        # Define payload
        self.payload = ["00"]



class ReadPumpBattery(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpBattery, self).__init__(device)

        # Define code
        self.code = "72"

        # Define payload
        self.payload = ["00"]



class ReadPumpReservoir(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpReservoir, self).__init__(device)

        # Define code
        self.code = "73"

        # Define payload
        self.payload = ["00"]



class ReadPumpStatus(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpStatus, self).__init__(device)

        # Define code
        self.code = "CE"

        # Define payload
        self.payload = ["00"]



class ReadPumpSettings(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpSettings, self).__init__(device)

        # Define code
        self.code = "C0"

        # Define payload
        self.payload = ["00"]



class ReadPumpBGUnits(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpBGUnits, self).__init__(device)

        # Define code
        self.code = "89"

        # Define payload
        self.payload = ["00"]



class ReadPumpCarbUnits(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpCarbUnits, self).__init__(device)

        # Define code
        self.code = "88"

        # Define payload
        self.payload = ["00"]



class ReadPumpBGTargets(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpBGTargets, self).__init__(device)

        # Define code
        self.code = "9F"

        # Define payload
        self.payload = ["00"]



class ReadPumpISF(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpISF, self).__init__(device)

        # Define code
        self.code = "8B"

        # Define payload
        self.payload = ["00"]



class ReadPumpCSF(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpCSF, self).__init__(device)

        # Define code
        self.code = "8A"

        # Define payload
        self.payload = ["00"]



class ReadPumpBasalProfileStandard(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpBasalProfileStandard, self).__init__(device)

        # Define code
        self.code = "92"

        # Define payload
        self.payload = ["00"]



class ReadPumpBasalProfileA(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpBasalProfileA, self).__init__(device)

        # Define code
        self.code = "93"

        # Define payload
        self.payload = ["00"]



class ReadPumpBasalProfileB(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpBasalProfileB, self).__init__(device)

        # Define code
        self.code = "94"

        # Define payload
        self.payload = ["00"]



class ReadPumpDailyTotals(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpDailyTotals, self).__init__(device)

        # Define code
        self.code = "79"

        # Define payload
        self.payload = ["00"]



class ReadPumpHistory(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpHistory, self).__init__(device)

        # Define code
        self.code = "80"

        # Define payload
        self.payload = ["00"]

        # FIXME: only send packet, do not wait for response?



class ReadPumpHistoryTest(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpHistoryTest, self).__init__(device)

        # Define code
        self.code = "80"

        # Define payload (numbers of bytes to come, page, zeros)
        self.payload = ["01"] + ["04"] + ["00"] * 63



class ReadPumpNext(PumpCommand):

    def __init__(self, device):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpNext, self).__init__(device)

        # Define code
        self.code = "06"

        # Define payload
        self.payload = ["00"]



def main():

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        MAIN
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """



# Run this when script is called from terminal
if __name__ == "__main__":
    main()