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
	usb_init();

	// Enable interrupts
	interrupts_enable();

    // Start timer
    timer_start();
}