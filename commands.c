#include "commands.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMMAND_GET
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
uint8_t command_get(void) {

	// Read command
	uint8_t cmd = usb_rx_byte();

	// Return it
	return cmd;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMMAND_DO
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void command_do(uint8_t cmd) {

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
		case 10:
			command_register_read();
			break;

		// Set register
		case 11:
			command_register_write();
			break;

		// Receive radio packets
		case 20:
			command_radio_receive();
			break;

		// Send radio packets
		case 21:
			command_radio_send();
			break;

		// Send and receive radio packets
		case 22:
			command_radio_send_receive();
			break;

		// Toggle LED
		case 30:
			command_led_toggle();
			break;

		// Turn LED on
		case 31:
			command_led_on();
			break;

		// Turn LED off
		case 32:
			command_led_off();
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

	// Initialize radio error
	uint8_t error = 0;

	// Get channel and timeout (ms)
	uint8_t channel = usb_rx_byte();
	uint32_t timeout = usb_rx_long();

	// Read bytes from radio and get error if there is one
	error = radio_receive(channel, timeout);

	// If error
	if (error != 0) {

        // Send error to master
        usb_tx_byte(error);
	}
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
    COMMAND_RADIO_SEND_RECEIVE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void command_radio_send_receive(void) {

	// Get channel, repeat and delay (ms) for sending part
	uint8_t tx_channel = usb_rx_byte();
	uint8_t tx_repeat = usb_rx_byte();
	uint32_t tx_delay = usb_rx_long();

	// Get channel and timeout (ms) for receiving part
	uint8_t rx_channel = usb_rx_byte();
	uint32_t rx_timeout = usb_rx_long();

	// Initialize radio error and retry count
	uint8_t error = 0;
	uint8_t retry = usb_rx_byte();

	// Send bytes to then receive some from radio
	radio_send(tx_channel, tx_repeat, tx_delay);

	// Read bytes from radio and get error if there is one
	error = radio_receive(rx_channel, rx_timeout);

	// Retry until no timeout and no retries left
	while (error == RADIO_ERROR_TIMEOUT && retry > 0) {

		// Resend packet in TX buffer
		radio_resend();

		// Read bytes from radio and get error if there is one
		error = radio_receive(rx_channel, rx_timeout);

		// Decrease retry count
		retry--;
	}

	// If error
	if (error != 0) {

        // Send error to master
        usb_tx_byte(error);
	}
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMMAND_LED_TOGGLE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void command_led_toggle(void) {

	// Toggle LED
	led_toggle();
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMMAND_LED_ON
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void command_led_on(void) {

	// Turn LED on
	led_on();
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMMAND_LED_OFF
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void command_led_off(void) {

	// Turn LED off
	led_off();
}