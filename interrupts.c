#include "interrupts.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    INTERRUPTS_ENABLE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void interrupts_enable(void) {

	// Reset all interrupt flags
	TCON = 0x05;
	S0CON = 0x00;
	S1CON = 0x00;
	IRCON = 0x00;
	IRCON2 = 0x00;

	// Enable interrupts globally
	EA = 1;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    INTERRUPTS_DISABLE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void interrupts_disable(void) {

	// Disable interrupts globally
	EA = 0;
}