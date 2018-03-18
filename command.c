#include "command.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMMAND_GET
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void command_get(void) {

	// Read command
	uint8_t cmd = usb_rx_byte();

	// Identify command
	switch (cmd) {

		// Get product
		case 0:
			usb_tx_bytes("CC1111", 6);
			break;

		// Get author
		case 1:
			usb_tx_bytes("keinechterdeutscher@gmail.com", 29);
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
			command_radio_receive();
			break;

		// Test command
		case 99:
			command_test();
			break;

		// Default (no command)
		default:
			usb_tx_bytes("N/A", 3);
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
	uint8_t addr = usb_rx_byte();
	uint8_t value = *radio_register(addr);

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
	uint8_t addr = usb_rx_byte();
	uint8_t value = usb_rx_byte();

	// Write register value
	*radio_register(addr) = value;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMMAND_RADIO_RECEIVE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void command_radio_receive(void) {

	// Get channel and timeout (ms)
	uint8_t channel = usb_rx_byte();
	uint32_t timeout = usb_rx_long();

	// Read bytes from radio
	radio_receive(channel, timeout);
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMMAND_RADIO_SEND
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void command_radio_send(void) {

	// Get channel, repeat and delay (ms)
	uint8_t channel = usb_rx_byte();
	uint8_t repeat = usb_rx_byte();
	uint32_t delay = usb_rx_long();

	// Send bytes to radio
	radio_send(channel, repeat, delay);
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMMAND_TEST
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void command_test(void) {

	// Get long word
	uint32_t test = usb_rx_long();

	// Repeat to master
	usb_tx_byte((test & 0xFF000000) >> (8*3));
	usb_tx_byte((test & 0x00FF0000) >> (8*2));
	usb_tx_byte((test & 0x0000FF00) >> (8*1));
	usb_tx_byte((test & 0x000000FF) >> (8*0));
}