#include "command.h"

void command_get(void) {

	// Read command
	uint8_t cmd = usb_get_byte();

	// Identify command
	switch (cmd) {

		// Get version
		case 57:
			usb_put_bytes("Hello World!\x00");
			break;

		// Test
		default:
			usb_put_bytes("N/A\x00");
			break;
	}
}