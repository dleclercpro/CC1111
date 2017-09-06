#include "radio.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_INIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_init(void) {

	// Power radio
	radio_power();

	// Enable radio interrupts
	radio_enable_interrupts();

}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_POWER
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_power(void) {

}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_ENABLE_INTERRUPTS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_enable_interrupts(void) {

	// Enable various RF interrupts
	RFIM = RFIM_IM_TXUNF | RFIM_IM_RXOVF | RFIM_IM_TIMEOUT | RFIM_IM_DONE |
		   RFIM_IM_CS | RFIM_IM_PQT | RFIM_IM_CCA | RFIM_IM_SFD;

	// Enable interrupts
	RFTXRXIE = 1;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_RFTXRX_ISR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_rftxrx_isr(void) __interrupt RFTXRX_VECTOR {

}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_GENERAL_ISR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_general_isr(void) __interrupt RF_VECTOR {

	// TX underflow
	if (RFIF & RFIF_IM_TXUNF) {

	}

	// RX overflow
	if (RFIF & RFIF_IM_RXOVF) {
		
	}

	// RX timeout
	if (RFIF & RFIF_IM_TIMEOUT) {
		
	}

	// Packet received/transmitted
	if (RFIF & RFIF_IM_DONE) {
		
	}

	// CS
	if (RFIF & RFIF_IM_CS) {
		
	}

	// PQT reached
	if (RFIF & RFIF_IM_PQT) {
		
	}

	// CCA
	if (RFIF & RFIF_IM_CCA) {
		
	}

	// SFD
	if (RFIF & RFIF_IM_SFD) {
		
	}
}