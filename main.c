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
	interrupts_init();

    // Start timer
    timer_start();

    // Loop
	/*
	while(1) {

	}
	*/
}