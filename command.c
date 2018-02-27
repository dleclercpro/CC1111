#include "command.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMMAND_GET
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void command_get(void) {

	// Read command
	uint8_t cmd = usb_get_byte();

	// Identify command
	switch (cmd) {

		// Get product
		case 0:
			usb_tx_bytes("CC1111");
			break;

		// Get author
		case 1:
			usb_tx_bytes("keinechterdeutscher@gmail.com");
			break;

		// Read register
		case 2:
			command_register_read();
			break;

		// Write register
		case 3:
			command_register_write();
			break;

		// Receive radio packets
		case 50:
			command_radio_read();
			break;

		// Default (no command)
		default:
			usb_tx_bytes("N/A");
			break;
	}
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMMAND_REGISTER_READ
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void command_register_read(void) {

	// Initialize register value
	uint8_t r;

	// Read register address
	uint8_t addr = usb_get_byte();

	// Get register value
	switch (addr) {

		// SYNC1
		case 0:
			r = SYNC1;
			break;

		// Default (incorrect address)
		default:
			r = 0;
			break;
	}

	// Return register value
	usb_tx_byte(r);
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMMAND_REGISTER_WRITE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void command_register_write(void) {

	// Read register address
	uint8_t addr = usb_get_byte();

	// Read register value
	uint8_t r = usb_get_byte();

	// Get register value
	switch (addr) {

		// SYNC1
		case 0:
			SYNC1 = r;
			break;

		// Default (incorrect address)
		default:
			r = 0;
			break;
	}
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMMAND_RADIO_READ
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void command_radio_read(void) {

	// Initialize flag
	uint8_t flag = 0;
	uint8_t channel = usb_get_byte();

	// Read radio
	flag = radio_read(channel, 250);

	// If no response (error flag)
	if (flag != 0) {

		// Send flag to master
		usb_tx_byte(flag);
	}

	else {
		usb_tx_byte(0);
	}
}