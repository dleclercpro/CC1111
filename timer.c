#include "timer.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    TIMER_INIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	Note: always read T1CNTL before T1CNTH!
*/
void timer_init(void) {

	// Suspend timer 1
	T1CTL = 0;

	// Reset its count
	T1CNTL = 0;

	// Define modulo
	T1CC0H = 0xFF;
	T1CC0L = 0xFF;

	// Resume it in modulo mode with divider
	T1CTL = T1CTL_MODE_MODULO;
}