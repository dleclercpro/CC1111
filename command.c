#include "command.h"

void command_get(void) {

	// Read command
	uint8_t cmd = usb_get_byte();

	// Identify command
	switch (cmd) {

		// Get version
		case 48:
			usb_put_bytes("Hello World!");
			break;

		// Get state
		case 49:
			usb_put_bytes("I <3 you! :)");
			break;

		// Test
		default:
			usb_put_bytes("N/A");
			break;
	}
}