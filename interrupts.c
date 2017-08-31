#include "interrupts.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    INTERRUPTS_INIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	Note: timer 1 CPU interrupt flag automatically cleared by hardware on ISR
		  entry.
*/
void interrupts_init(void) {

	// Reset interrupts
	interrupts_reset();

	// Enable timer 1 channel 0 compare interrupts
	T1CCTL0 = T1CCTL_NO_CAPTURE | T1CCTL_MODE_COMPARE | T1CCTL_CMP_SET | T1CCTL_IM_ENABLED | T1CCTL_CPSEL_NORMAL;

	// Enable timer 1 overflow interrupts
	OVFIM = 1;

	// Enable timer 1 interrupts
	T1IE = 1;

	// Enable interrupts globally
	EA = 1;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    INTERRUPTS_RESET
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void interrupts_reset(void) {

	// Reset all interrupt flags
	TCON = 0x05;
	S0CON = 0x00;
	S1CON = 0x00;
	IRCON = 0x00;
	IRCON2 = 0x00;
}