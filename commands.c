#include "commands.h"

void command_get() {

	// Initialize command
	uint8_t command = 0;

	// Read bytes from USB
	usb_receive_bytes_bulk();

	// Parse command
	command = 0;
}