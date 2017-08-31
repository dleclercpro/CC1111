#include "interrupts.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    INTERRUPTS_INIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void interrupts_init(void) {

	// Reset all interrupt flags
	TCON = 0x05;
	S0CON = 0x00;
	S1CON = 0x00;
	IRCON = 0x00;
	IRCON2 = 0x00;

	// Enable interrupts globally
	EA = 1;
}