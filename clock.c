#include "clock.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    CLOCK_INIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void clock_init(void) {

	// Define speed mask and value
	// CC1111's crystal oscillator reference frequency: 24 MHz
	// Timer tick: 24 MHz
	const uint8_t speed_mask = CLKCON_TICKSPD_MASK | CLKCON_CLKSPD_MASK;
	const uint8_t speed_value = CLKCON_TICKSPD_1 | CLKCON_CLKSPD_1;
	
	// Power up both oscillators
	SLEEP &= ~SLEEP_OSC_PD;

	// Use crystal oscillator as system clock 
	CLKCON &= ~CLKCON_OSC_MASK;

	// Wait until system clock is set
	while (CLKCON & CLKCON_OSC_MASK) {
		NOP();
	}

	// Set system clock speed
	CLKCON = (CLKCON & ~speed_mask) | speed_value;

	// Wait until speed is set
	while ((CLKCON & speed_mask) != speed_value) {
		NOP();
	}

	// Wait until crystal oscillator is stable
	while ((SLEEP & SLEEP_XOSC_STB) != SLEEP_XOSC_STB) {
		NOP();
	}

	// Power down unused RC oscillator
	SLEEP |= SLEEP_OSC_PD;
}