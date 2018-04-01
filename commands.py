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
import datetime



# USER LIBRARIES
import lib
import errors
import packets



# CONSTANTS
PUMP_BOLUS_RATE = 40.0 # Bolus delivery rate (s/U)
PUMP_BOLUS_STROKE = 0.1
PUMP_BASAL_STROKE = 0.025
PUMP_BASAL_TIME_BLOCK = 30 # (m)



# CLASSES
class Command(object):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Store stick instance
        self.stick = stick

        # Initialize code
        self.code = None

        # Initialize resettable command characteristics
        self.reset()



    def reset(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RESET
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Reset response
        self.response = None

        # Reset data
        self.data = {"TX": None,
                     "RX": None}



    def encode(self, *args):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ENCODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Ignore
        pass



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Ignore
        pass



    def send(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            SEND
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Ignore
        pass



    def receive(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RECEIVE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Ignore
        pass



    def execute(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            EXECUTE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Send command
        self.send()

        # Receive response
        self.receive()



    def store(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            STORE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Ignore
        pass



    def run(self, *args):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RUN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            When command runned, its core is executed, then the received data
            (if any) is decoded, and returned.
        """

        # Reset command
        self.reset()

        # Encode parameters
        self.encode(*args)

        # Execute command
        self.execute()

        # Decode it
        self.decode()

        # Return it
        return self.response



class StickCommand(Command):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(StickCommand, self).__init__(stick)



    def send(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            SEND
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Send command code
        self.stick.write(self.code)



    def receive(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RECEIVE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Get data
        self.data["RX"] = self.stick.read()



class ReadStickName(StickCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadStickName, self).__init__(stick)

        # Define code
        self.code = 0



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Decode data
        self.response = "".join(lib.charify(self.data["RX"]))

        # Info
        print "Stick name: " + self.response



class ReadStickAuthor(StickCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadStickAuthor, self).__init__(stick)

        # Define code
        self.code = 1



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Decode data
        self.response = "".join(lib.charify(self.data["RX"]))

        # Info
        print "Stick author: " + self.response



class ReadStickRadioRegister(StickCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadStickRadioRegister, self).__init__(stick)

        # Define code
        self.code = 10



    def reset(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RESET
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize resetting
        super(ReadStickRadioRegister, self).reset()

        # Reset register
        self.register = None

        # Reset register address
        self.address = None



    def encode(self, register):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ENCODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Store register
        self.register = register

        # Get register address
        self.address = self.stick.registers.index(register)



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Decode data
        self.response = self.data["RX"][0]

        # Info
        print self.register + ": " + str(self.response)



    def send(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            SEND
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Send command code
        self.stick.write(self.code)

        # Send register address
        self.stick.write(self.address)



class WriteStickRadioRegister(StickCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(WriteStickRadioRegister, self).__init__(stick)

        # Define code
        self.code = 11



    def reset(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RESET
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize resetting
        super(WriteStickRadioRegister, self).reset()

        # Reset register
        self.register = None

        # Reset register address
        self.address = None

        # Reset register value
        self.value = None



    def encode(self, register, value):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ENCODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Store register
        self.register = register

        # Get register address
        self.address = self.stick.registers.index(register)

        # Store register value
        self.value = value



    def send(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            SEND
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Send command code
        self.stick.write(self.code)

        # Send register address
        self.stick.write(self.address)

        # Send value
        self.stick.write(self.value)



    def receive(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RECEIVE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Ignore
        pass



class ReadStickRadio(StickCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadStickRadio, self).__init__(stick)

        # Define code
        self.code = 20



    def reset(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RESET
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize resetting
        super(ReadStickRadio, self).reset()

        # Reset channel
        self.channel = None

        # Reset timeout values
        self.timeout = None        



    def encode(self, channel = 0, timeout = 500, tolerate = False):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ENCODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Store channel
        self.channel = channel

        # Store timeout values
        self.timeout = {"Stick": timeout + 500,
                        "Radio": lib.pack(timeout, 4)}

        # Store error tolerance
        self.tolerate = tolerate



    def send(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            SEND
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Send command code
        self.stick.write(self.code)

        # Send channel
        self.stick.write(self.channel)

        # Send radio timeout
        self.stick.write(self.timeout["Radio"])



    def receive(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RECEIVE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Try
        try:

            # Get data (remove EOP byte)
            self.data["RX"] = self.stick.read(timeout = self.timeout["Stick"],
                                              radio = True)[:-1]

        # If radio error
        except errors.RadioError:

            # Errors not tolerated
            if not self.tolerate:

                # Stop
                raise



class WriteStickRadio(StickCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(WriteStickRadio, self).__init__(stick)

        # Define code
        self.code = 21



    def reset(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RESET
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize resetting
        super(WriteStickRadio, self).reset()

        # Reset channel
        self.channel = None

        # Reset repeat count
        self.repeat = None

        # Reset repeat delay
        self.delay = None



    def encode(self, data, channel = 0, repeat = 0, delay = 0):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ENCODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Store data
        self.data["TX"] = data

        # Store channel
        self.channel = channel

        # Store repeat count
        self.repeat = repeat

        # Store repeat delay
        self.delay = lib.pack(delay, 4)



    def send(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            SEND
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Send command code
        self.stick.write(self.code)

        # Send channel
        self.stick.write(self.channel)

        # Send delay
        self.stick.write(self.delay)

        # Send data
        self.stick.write(self.data["TX"])

        # Send last byte
        self.stick.write(0)



    def receive(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RECEIVE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Ignore
        pass



class WriteReadStickRadio(StickCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(WriteReadStickRadio, self).__init__(stick)

        # Define code
        self.code = 22



    def reset(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RESET
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize resetting
        super(WriteReadStickRadio, self).reset()

        # Reset channel values
        self.channel = None

        # Reset write repeat count
        self.repeat = None

        # Reset write repeat delay
        self.delay = None

        # Reset retry count
        self.retry = None

        # Reset timeout values
        self.timeout = None

        # Reset error tolerance
        self.tolerate = None



    def encode(self, data, channelTX = 0, channelRX = 0, repeat = 1, delay = 0,
                     retry = 1, timeout = 500, tolerate = False):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ENCODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Store data
        self.data["TX"] = data

        # Store channel values
        self.channel = {"TX": channelTX,
                        "RX": channelRX}

        # Store write repeat count
        self.repeat = repeat

        # Store write repeat delay
        self.delay = lib.pack(delay, 4)

        # Store retry count
        self.retry = retry

        # Store timeout values
        self.timeout = {"Stick": (retry + 1) * timeout + 500,
                        "Radio": lib.pack(timeout, 4)}

        # Store error tolerance
        self.tolerate = tolerate



    def send(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            SEND
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Send command code
        self.stick.write(self.code)

        # Send write channel
        self.stick.write(self.channel["TX"])

        # Send repeat count
        self.stick.write(self.repeat)

        # Send send repeat delay
        self.stick.write(self.delay)

        # Send read channel
        self.stick.write(self.channel["RX"])

        # Send radio timeout
        self.stick.write(self.timeout["Radio"])

        # Send retry count
        self.stick.write(self.retry)

        # Send packet
        self.stick.write(self.data["TX"])

        # Send last byte
        self.stick.write(0)



    def receive(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RECEIVE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Try
        try:

            # Get data (remove EOP byte)
            self.data["RX"] = self.stick.read(timeout = self.timeout["Stick"],
                                              radio = True)[:-1]

        # If radio error
        except errors.RadioError:

            # Errors not tolerated
            if not self.tolerate:

                # Stop
                raise



class FlashStickLED(StickCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(FlashStickLED, self).__init__(stick)

        # Define code
        self.code = 30



class PumpCommand(Command):

    def reset(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RESET
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize resetting
        super(PumpCommand, self).reset()

        # Reset data
        self.data = {"TX": [],
                     "RX": []}

        # Reset packets
        self.packets = {"TX": [],
                        "RX": []}

        # Reset parameters
        self.parameters = ["00"]



    def send(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            SEND
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Generate packet to send to pump
        pkt = packets.ToPumpPacket(self.code, self.parameters)

        # Store it
        self.packets["TX"].append(pkt)

        # Send encoded packet
        self.stick.commands["Radio TX/RX"].run(pkt.bytes["Encoded"])



    def receive(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RECEIVE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Store data
        self.data["RX"].append(self.stick.commands["Radio TX/RX"].data["RX"])



class PumpSetCommand(PumpCommand):

    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize decoding
        super(PumpSetCommand, self).decode()

        # Get last packet
        pkt = self.packets["RX"][-1]

        # Define command ACK
        ack = [pkt.code] + pkt.payload

        # Unsuccessful
        if ack != ["06", "00"]:

            # Raise error
            raise errors.UnsuccessfulRadioCommand



    def receive(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RECEIVE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize receiving of packet
        super(PumpSetCommand, self).receive()

        # Parse data into packet
        pkt = packets.FromPumpACKPacket(self.data["RX"][-1])

        # Show it
        pkt.show()

        # Store it
        self.packets["RX"].append(pkt)



class PumpNormalGetCommand(PumpCommand):

    def receive(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RECEIVE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize receiving packet
        super(PumpNormalGetCommand, self).receive()

        # Parse data into packet
        pkt = packets.FromPumpNormalPacket(self.data["RX"][-1])

        # Show it
        pkt.show()

        # Store it
        self.packets["RX"].append(pkt)



class PumpBigGetCommand(PumpCommand):

    def receive(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RECEIVE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize receiving packet
        super(PumpBigGetCommand, self).receive()

        # Parse data into packet
        pkt = packets.FromPumpBigPacket(self.data["RX"][-1])

        # Show it
        pkt.show()

        # Store it
        self.packets["RX"].append(pkt)



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Get last packets
        pkts = self.packets["RX"][1:]

        # Decode payload
        payload = lib.dehexify(lib.flatten([pkt.payload for pkt in pkts]))

        # Return it for further decoding
        return payload



class PumpBigCommand(PumpCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(PumpBigCommand, self).__init__(stick)

        # Define number of times pre-/postlude commands need to be executed
        self.size = {"Prelude": 1,
                     "Postlude": 0}



    def prelude(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            PRELUDE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Execute prelude command
        self.execute()

        # Decode it
        self.decode()



    def postlude(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            POSTLUDE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Get postlude command
        cmd = ReadPumpMore(self.stick)

        # Run postlude command given number of times
        for i in range(self.size["Postlude"]):

            # Do it
            cmd.run()

            # Store response packet
            self.packets["RX"].append(cmd.packets["RX"][-1])



    def run(self, *args):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            RUN
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Reset command
        self.reset()

        # Execute prelude
        self.prelude()

        # Encode parameters
        self.encode(*args)

        # Execute command core
        self.execute()

        # Execute postlude
        self.postlude()

        # Decode it
        self.decode()

        # Return response
        return self.response



class ReadPumpTime(PumpNormalGetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpTime, self).__init__(stick)

        # Define code
        self.code = "70"



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Get last packet
        pkt = self.packets["RX"][-1]

        # Decode payload
        payload = lib.dehexify(pkt.payload)

        # Destructure
        [h, m, s, Y1, Y2, M, D] = payload[0:7]

        # Unpack year
        Y = lib.unpack([Y1, Y2])

        # Store formatted time
        self.response = lib.formatTime(datetime.datetime(Y, M, D, h, m, s))

        # Show response
        print "Time: " + str(self.response)



class ReadPumpModel(PumpNormalGetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpModel, self).__init__(stick)

        # Define code
        self.code = "8D"



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Get last packet
        pkt = self.packets["RX"][-1]

        # Decode payload
        payload = lib.charify(lib.dehexify(pkt.payload))

        # Decode
        self.response = int("".join(payload[1:4]))

        # Show response
        print "Model: " + str(self.response)



class ReadPumpFirmware(PumpNormalGetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpFirmware, self).__init__(stick)

        # Define code
        self.code = "74"



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Get last packet
        pkt = self.packets["RX"][-1]

        # Decode payload
        payload = lib.charify(lib.dehexify(pkt.payload))

        # Decode
        self.response = "".join(payload[0:8] + [" "] + payload[8:11])

        # Show response
        print "Firmware: " + str(self.response)



class ReadPumpBattery(PumpNormalGetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpBattery, self).__init__(stick)

        # Define code
        self.code = "72"



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Get last packet
        pkt = self.packets["RX"][-1]

        # Decode payload
        payload = lib.dehexify(pkt.payload)

        # Decode
        self.response = round(lib.unpack(payload[1:3]) / 100.0, 2)

        # Show response
        print "Battery: " + str(self.response) + " V"



class ReadPumpReservoir(PumpNormalGetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpReservoir, self).__init__(stick)

        # Define code
        self.code = "73"



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Get last packet
        pkt = self.packets["RX"][-1]

        # Decode payload
        payload = lib.dehexify(pkt.payload)

        # Decode
        self.response = round(lib.unpack(payload[0:2]) * PUMP_BOLUS_STROKE, 1)

        # Show response
        print "Reservoir: " + str(self.response) + " U"



class ReadPumpStatus(PumpNormalGetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpStatus, self).__init__(stick)

        # Define code
        self.code = "CE"



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Get last packet
        pkt = self.packets["RX"][-1]

        # Decode payload
        payload = lib.dehexify(pkt.payload)

        # Decode
        self.response = {"Normal": payload[0] == 3,
                         "Bolusing": payload[1] == 1,
                         "Suspended": payload[2] == 1}

        # Show response
        print "Status: " + str(self.response)



class ReadPumpSettings(PumpNormalGetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpSettings, self).__init__(stick)

        # Define code
        self.code = "C0"



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Get last packet
        pkt = self.packets["RX"][-1]

        # Decode payload
        payload = lib.dehexify(pkt.payload)

        # Decode
        self.response = {"DIA": payload[17],
                         "Max Bolus": payload[5] * PUMP_BOLUS_STROKE,
                         "Max Basal": lib.unpack(payload[6:8]) *
                                      PUMP_BASAL_STROKE}

        # Show response
        print "Settings: " + str(self.response)



class ReadPumpBGUnits(PumpNormalGetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpBGUnits, self).__init__(stick)

        # Define code
        self.code = "89"



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Get last packet
        pkt = self.packets["RX"][-1]

        # Decode payload
        payload = lib.dehexify(pkt.payload)

        # Decode
        # mg/dL
        if payload[0] == 1:

            # Store response
            self.response = "mg/dL"

        # mmol/L
        elif payload[0] == 2:

            # Store response
            self.response = "mmol/L"

        # Show response
        print "BG Units: " + str(self.response)



class ReadPumpCarbsUnits(PumpNormalGetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpCarbsUnits, self).__init__(stick)

        # Define code
        self.code = "88"



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Get last packet
        pkt = self.packets["RX"][-1]

        # Decode payload
        payload = lib.dehexify(pkt.payload)

        # Decode
        # mg/dL
        if payload[0] == 1:

            # Store response
            self.response = "g"

        # mmol/L
        elif payload[0] == 2:

            # Store response
            self.response = "exchange"

        # Show response
        print "Carbs Units: " + str(self.response)



class ReadPumpBGTargets(PumpNormalGetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpBGTargets, self).__init__(stick)

        # Define code
        self.code = "9F"



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Get last packet
        pkt = self.packets["RX"][-1]

        # Decode payload
        payload = lib.dehexify(pkt.payload)

        # Initialize response
        self.response = {"Times": [],
                         "Targets": [],
                         "Units": None}

        # Define size of entry
        size = 3

        # Decode units
        # mg/dL
        if payload[0] == 1:

            # Store them
            self.response["Units"] = "mg/dL"

            # Define byte multiplicator
            m = 0

        # mmol/L
        elif payload[0] == 2:

            # Store them
            self.response["Units"] = "mmol/L"

            # Define byte multiplicator
            m = 1.0

        # Compute number of targets
        n = (pkt.size - 1) / size

        # Decode targets
        for i in range(n):

            # Update index
            i *= size

            # Decode time (m)
            t = payload[i + 1] * PUMP_BASAL_TIME_BLOCK

            # Convert it to hours and minutes
            t = "{0:02}".format(t / 60) + ":" + "{0:02}".format(t % 60)

            # Store it
            self.response["Times"].append(t)

            # Decode target
            self.response["Targets"].append([payload[i + 2] / 10 ** m,
                                             payload[i + 3] / 10 ** m])

        # Show response
        print "BG Targets: " + str(self.response)



class ReadPumpFactors(PumpNormalGetCommand):

    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Get last packet
        pkt = self.packets["RX"][-1]

        # Decode payload
        payload = lib.dehexify(pkt.payload)

        # Initialize response
        self.response = {"Times": [],
                         "Factors": [],
                         "Units": None}

        # Define size of entry
        size = 2

        # Compute number of targets
        n = (pkt.size - 1) / size

        # Define decoding factor
        # Integer
        if payload[0] == 1:

            # Do it
            m = 0

        # Float
        elif payload[0] == 2:

            # Do it
            m = 1.0

        # Decode targets
        for i in range(n):

            # Update index
            i *= size

            # Decode time (m)
            t = payload[i + 1] % 64 * PUMP_BASAL_TIME_BLOCK

            # Convert it to hours and minutes
            t = "{0:02}".format(t / 60) + ":" + "{0:02}".format(t % 60)

            # Store it
            self.response["Times"].append(t)

            # Decode factor
            f = lib.unpack([payload[i + 1] / 64, payload[i + 2]]) / 10 ** m

            # Store it
            self.response["Factors"].append(f)

        # Return payload for further decoding
        return payload



class ReadPumpISF(ReadPumpFactors):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpISF, self).__init__(stick)

        # Define code
        self.code = "8B"



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize decoding and get payload
        payload = super(ReadPumpISF, self).decode()

        # Decode units
        # mg/dL
        if payload[0] == 1:

            # Store them
            self.response["Units"] = "mg/dL/U"

        # mmol/L
        elif payload[0] == 2:

            # Store them
            self.response["Units"] = "mmol/L/U"

        # Show response
        print "ISF: " + str(self.response)



class ReadPumpCSF(ReadPumpFactors):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpCSF, self).__init__(stick)

        # Define code
        self.code = "8A"



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize decoding and get payload
        payload = super(ReadPumpCSF, self).decode()

        # Decode units
        # mg/dL
        if payload[0] == 1:

            # Store them
            self.response["Units"] = "g/U"

        # mmol/L
        elif payload[0] == 2:

            # Store them
            self.response["Units"] = "U/exchange"

        # Show response
        print "CSF: " + str(self.response)



class ReadPumpBasalProfile(PumpBigCommand, PumpBigGetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpBasalProfile, self).__init__(stick)

        # Define postlude command repeat count
        self.size["Postlude"] = 1



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize decoding and get whole payload
        payload = super(ReadPumpBasalProfile, self).decode()

        # Initialize response
        self.response = {"Times": [],
                         "Rates": []}

        # Define size of entry
        size = 3

        # Compute number of targets
        n = (len(payload) - 1) / size

        # Initialize index
        i = 0

        # Decode targets
        while True:

            # Define start (a) and end (b) indices of current entry based
            # on the latter's size
            a = n * i
            b = a + n

            # Get entry
            entry = payload[a:b]

            # No more data in payload
            if sum(entry) == 0 or len(entry) != n:

                # Exit
                break

            # Decode time (m)
            t = entry[2] * PUMP_BASAL_TIME_BLOCK

            # Convert it to hours and minutes
            t = "{0:02}".format(t / 60) + ":" + "{0:02}".format(t % 60)

            # Store it
            self.response["Times"].append(t)

            # Decode rate
            r = lib.unpack([entry[0], entry[1]], "<") / PUMP_BOLUS_RATE

            # Store it
            self.response["Rates"].append(r)

            # Update index
            i += 1



class ReadPumpBasalProfileStandard(ReadPumpBasalProfile):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpBasalProfileStandard, self).__init__(stick)

        # Define code
        self.code = "92"



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize decoding
        super(ReadPumpBasalProfileStandard, self).decode()

        # Show response
        print "Basal Profile (Standard): " + str(self.response)



class ReadPumpBasalProfileA(ReadPumpBasalProfile):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpBasalProfileA, self).__init__(stick)

        # Define code
        self.code = "93"



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize decoding
        super(ReadPumpBasalProfileA, self).decode()

        # Show response
        print "Basal Profile (A): " + str(self.response)



class ReadPumpBasalProfileB(ReadPumpBasalProfile):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpBasalProfileB, self).__init__(stick)

        # Define code
        self.code = "94"



    def decode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            DECODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize decoding
        super(ReadPumpBasalProfileB, self).decode()

        # Show response
        print "Basal Profile (B): " + str(self.response)



class ReadPumpDailyTotals(PumpNormalGetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpDailyTotals, self).__init__(stick)

        # Define code
        self.code = "79"



class ReadPumpTB(PumpNormalGetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpTB, self).__init__(stick)

        # Define code
        self.code = "98"



class ReadPumpHistorySize(PumpNormalGetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpHistorySize, self).__init__(stick)

        # Define code
        self.code = "9D"



class ReadPumpHistoryPage(PumpBigCommand, PumpBigGetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpHistoryPage, self).__init__(stick)

        # Define code
        self.code = "80"

        # Define postlude command repeat count
        self.size["Postlude"] = 14



    def encode(self, page = 0):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ENCODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Test page number
        lib.checkIntWithinRange(page, [0, 35], "Invalid history page number.")

        # Define number of bytes to read from payload
        self.parameters = ["01"] + 64 * ["00"]

        # Define page
        self.parameters[1] = "{0:02X}".format(page)



class ReadPumpMore(PumpBigGetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ReadPumpMore, self).__init__(stick)

        # Define code
        self.code = "06"



class PowerPump(PumpBigCommand, PumpSetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(PowerPump, self).__init__(stick)

        # Define code
        self.code = "5D"

        # Define prelude command repeat counts
        self.size["Prelude"] = 50



    def prelude(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            PRELUDE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Execute a given number of times
        for i in range(self.size["Prelude"]):

            # Try
            try:

                # Execute
                self.execute()

                # Decode
                self.decode()

                # Exit
                return

            # Except
            except errors.RadioError, errors.InvalidPacket:

                # Ignore
                pass

        # Pump absent?
        raise errors.NoPump



    def encode(self, t = 10):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ENCODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Test RF session length
        lib.checkIntWithinRange(t, [0, 30], "Invalid RF session length.")

        # Define number of bytes to read from payload
        self.parameters = ["02"] + 64 * ["00"]

        # Define arbitrary byte
        self.parameters[1] = "01"

        # Define button
        self.parameters[2] = "{0:02X}".format(t)



class PushPumpButton(PumpBigCommand, PumpSetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(PushPumpButton, self).__init__(stick)

        # Define code
        self.code = "5B"



    def encode(self, button = "DOWN"):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ENCODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Try
        try:

            # Get button corresponding byte
            button = ["EASY", "ESC", "ACT", "UP", "DOWN"].index(button)

        # Except
        except ValueError:

            # Raise error
            raise IOError("Bad button.")

        # Define number of bytes to read from payload
        self.parameters = ["01"] + 64 * ["00"]

        # Define button
        self.parameters[1] = "{0:02X}".format(button)



class ResumePump(PumpBigCommand, PumpSetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(ResumePump, self).__init__(stick)

        # Define code
        self.code = "4D"



    def encode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ENCODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Define number of bytes to read from payload
        self.parameters = ["01"] + 64 * ["00"]

        # Define button
        self.parameters[1] = "00"



class SuspendPump(PumpBigCommand, PumpSetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(SuspendPump, self).__init__(stick)

        # Define code
        self.code = "4D"



    def encode(self):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ENCODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Define number of bytes to read from payload
        self.parameters = ["01"] + 64 * ["00"]

        # Define button
        self.parameters[1] = "01"



class DeliverPumpBolus(PumpBigCommand, PumpSetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(DeliverPumpBolus, self).__init__(stick)

        # Define code
        self.code = "42"



    def encode(self, bolus = 0):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ENCODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Encode bolus
        bolus *= 10.0

        # Test bolus
        lib.checkIntWithinRange(bolus, [0, 250], "Invalid bolus.")

        # Convert bolus to integer
        bolus = int(bolus)

        # Define number of bytes to read from payload
        self.parameters = ["01"] + 64 * ["00"]

        # Define bolus
        self.parameters[1] = "{0:02X}".format(bolus)



class SetPumpTBUnits(PumpBigCommand, PumpSetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(SetPumpTBUnits, self).__init__(stick)

        # Define code
        self.code = "68"



    def encode(self, units = "U/h"):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ENCODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Try
        try:

            # Get unit corresponding byte
            units = ["U/h", "%"].index(units)

        # Except
        except ValueError:

            # Raise error
            raise IOError("Bad TB units.")

        # Define number of bytes to read from payload
        self.parameters = ["01"] + 64 * ["00"]

        # Define units
        self.parameters[1] = "{0:02X}".format(units)



class SetPumpAbsoluteTB(PumpBigCommand, PumpSetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(SetPumpAbsoluteTB, self).__init__(stick)

        # Define code
        self.code = "4C"



    def encode(self, rate = 0, duration = 0):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ENCODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Encode rate (divide by pump stroke)
        rate = round(rate / 0.025)

        # Encode duration (divide by time block)
        duration /= 30.0

        # Test rate
        lib.checkIntWithinRange(rate, [0, 1400], "Invalid TB rate.")

        # Test duration
        lib.checkIntWithinRange(duration, [0, 48], "Invalid TB duration.")

        # Convert rate to integer
        rate = int(rate)

        # Convert duration to integer
        duration = int(duration)

        # Define number of bytes to read from payload
        self.parameters = ["03"] + 64 * ["00"]

        # Define rate
        self.parameters[1:3] = ["{0:02X}".format(x) for x in lib.pack(rate, 2)]

        # Define duration
        self.parameters[3] = "{0:02X}".format(duration)



class SetPumpPercentageTB(PumpBigCommand, PumpSetCommand):

    def __init__(self, stick):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            INIT
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Initialize command
        super(SetPumpPercentageTB, self).__init__(stick)

        # Define code
        self.code = "69"



    def encode(self, rate = 0, duration = 0):

        """
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            ENCODE
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        # Encode duration (divide by time block)
        duration /= 30.0

        # Test rate
        lib.checkIntWithinRange(rate, [0, 200], "Invalid TB rate.")

        # Test duration
        lib.checkIntWithinRange(duration, [0, 48], "Invalid TB duration.")

        # Convert rate to integer
        rate = int(rate)

        # Convert duration to integer
        duration = int(duration)

        # Define number of bytes to read from payload
        self.parameters = ["02"] + 64 * ["00"]

        # Define rate
        self.parameters[1] = "{0:02X}".format(rate)

        # Define duration
        self.parameters[2] = "{0:02X}".format(duration)



def main():

    """
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        MAIN
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """



# Run this when script is called from terminal
if __name__ == "__main__":
    main()