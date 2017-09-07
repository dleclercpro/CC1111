#include "main.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    MAIN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void main (void) {

    // Initialize stuff
	clock_init();
	timer_init();
	led_init();

	// Enable interrupts
	interrupts_enable();

    // Start timer
    timer_start();

    // Initialize components
    usb_init();
    radio_init();
}