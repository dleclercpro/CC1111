#include "clock.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    CLOCK_INIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void clock_init() {

	// Define speed mask and value
	// CC1111's crystal oscillator reference frequency: 24 MHz
	// Here choosing reference frequency for clock and tick speed
	const uint8_t speed_mask = CLKCON_TICKSPD_MASK | CLKCON_CLKSPD_MASK;
	const uint8_t speed_value = CLKCON_TICKSPD_1 | CLKCON_CLKSPD_1;
	
	// Power up both oscillators (force oscillator bit to 0 and let the rest
	// like it is)
	SLEEP &= ~SLEEP_OSC_PD;

	// Set system clock to crystal oscillator
	CLKCON &= ~CLKCON_OSC_MASK;

	// Wait until clock is switched (use mask to have all zeros when bit is set)
	while (CLKCON & CLKCON_OSC_MASK) {
		NOP();
	}

	// Set system clock speed (reset it, then set new value)
	CLKCON = (CLKCON & ~speed_mask) | speed_value;

	// Wait until speed is set (isolate speeds with mask and compare to value)
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