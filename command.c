#include "command.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMMAND_GET
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void command_get(void) {

	// Read command
	uint8_t cmd = usb_get_byte();

	// Switch LED
	//led_switch();

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

		// Get register
		case 2:
			command_register_read();
			break;

		// Set register
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

	// Read register address and value
	uint8_t addr = usb_get_byte();
	uint8_t value = *radio_register_link(addr);

	// Send register value to master
	usb_tx_byte(value);
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMMAND_REGISTER_WRITE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void command_register_write(void) {

	// Read register address and value
	uint8_t addr = usb_get_byte();
	uint8_t value = usb_get_byte();

	// Write register value
	*radio_register_link(addr) = value;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMMAND_RADIO_READ
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void command_radio_read(void) {

	// Initialize channel and timeout (s)
	uint8_t channel = usb_get_byte();
	uint8_t timeout = usb_get_byte();

	// Read radio
	radio_read(channel, timeout);
}