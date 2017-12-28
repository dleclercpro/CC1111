#include "command.h"

void command_get(void) {

	// Read command
	uint8_t cmd = usb_get_byte();

	// Identify command
	switch (cmd) {

		// Get version
		case 57:
			usb_put_byte('H');
			usb_put_byte('e');
			usb_put_byte('l');
			usb_put_byte('l');
			usb_put_byte('o');
			usb_put_byte(' ');
			usb_put_byte('W');
			usb_put_byte('o');
			usb_put_byte('r');
			usb_put_byte('l');
			usb_put_byte('d');
			usb_put_byte('!');
			usb_flush_bytes();
			break;

		// Test
		default:
			usb_put_byte('T');
			usb_put_byte('e');
			usb_put_byte('s');
			usb_put_byte('t');
			usb_flush_bytes();
			break;
	}

	// LED test
	led_switch();
}