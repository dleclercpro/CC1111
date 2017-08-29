#include "clock.h"
#include "led.h"
#include "main.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    MAIN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void main () {

    // Initialize stuff
	clock_init();
	timer_init();
    led_init();

    // Loop
	while(1) {

		// If timer has reached modulo
		if ((T1CTL & T1CTL_OVFIF) == T1CTL_OVFIF) {

	        // Switch LED
			led_switch();

			// Reset timer overflow flag
			T1CTL &= ~T1CTL_OVFIF;
		}

        // Wait
		//delay(100);
	}
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	DELAY
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void delay (int t) {

	int i, j;

	for (i = 0; i < t; i++) {
		for (j = 0; j < 1000; j++) {

		}
	}
}
