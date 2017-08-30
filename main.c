#include "clock.h"
#include "interrupts.h"
#include "timer.h"
#include "led.h"
#include "lib.h"
#include "main.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    MAIN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void main (void) {

    // Initialize stuff
	clock_init();
	interrupts_init();
	timer_init();
    led_init();

    // Loop
	while(1) {

		// If timer has reached modulo
		if (T1CTL & T1CTL_OVFIF) {

	        // Switch LED
			led_switch();

			// Reset timer overflow flag
			T1CTL &= ~T1CTL_OVFIF;
		}

        // Wait
		//delay(500);
	}
}