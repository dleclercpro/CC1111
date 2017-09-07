#include "radio.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_INIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_init(void) {

	// Power radio
	radio_power();

	// Configure radio
	radio_configure();

	// Enable radio interrupts
	radio_enable_interrupts();
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_POWER
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_power(void) {
	NOP();
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

	// Enable RF interrupts
	RFTXRXIE = 1;

    // Enable interrupts
    IEN2 |= IEN2_RFIE;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_CONFIGURE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_configure(void) {

	// Configure radio
	SYNC1 = 	0xFF;
	SYNC0 = 	0x00;
	PKTLEN = 	0xFF;
	PKTCTRL1 = 	0x00;
	PKTCTRL0 = 	0x00;
	ADDR = 		0x00;
	FSCTRL1 = 	0x06;
	FSCTRL0 = 	0x00;
	MDMCFG4 = 	0x99;
	MDMCFG3 = 	0x66;
	MDMCFG2 = 	0x33;
	MDMCFG1 = 	0x61;
	MDMCFG0 = 	0x7E;
	DEVIATN = 	0x15;
	MCSM2 = 	0x07;
	MCSM1 = 	0x30;
	MCSM0 = 	0x18;
	FOCCFG = 	0x17;
	FREND1 = 	0xB6;
	FREND0 = 	0x11;
	FSCAL3 = 	0xE9;
	FSCAL2 = 	0x2A;
	FSCAL1 = 	0x00;
	FSCAL0 = 	0x1F;
	TEST1 = 	0x31;
	TEST0 = 	0x09;
	PA_TABLE0 = 0x00;
	AGCCTRL2 = 	0x07;
	AGCCTRL1 = 	0x00;
	AGCCTRL0 = 	0x91;

	// Radio locale
	// North America (NA)
	#if RADIO_LOCALE == RADIO_LOCALE_NA
		FREQ2 = 	0x26;
		FREQ1 = 	0x30;
		FREQ0 = 	0x70;
		CHANNR = 	0x02;
		PA_TABLE1 = 0xC0;
	// Worldwide (WW)
	#elif RADIO_LOCALE == RADIO_LOCALE_WW
		FREQ2 = 	0x24;
		FREQ1 = 	0x2E;
		FREQ0 = 	0x38;
		CHANNR = 	0x00;
		PA_TABLE1 = 0xC2;
	#endif
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

		// Enter IDLE state
		RFST = RFST_SIDLE;
	}

	// RX overflow
	if (RFIF & RFIF_IM_RXOVF) {

		// Enter IDLE state
		RFST = RFST_SIDLE;		
	}

	// RX timeout
	if (RFIF & RFIF_IM_TIMEOUT) {
		NOP();
	}

	// Packet received/transmitted
	if (RFIF & RFIF_IM_DONE) {
		NOP();
	}

	// CS
	if (RFIF & RFIF_IM_CS) {
		NOP();
	}

	// PQT reached
	if (RFIF & RFIF_IM_PQT) {
		NOP();
	}

	// CCA
	if (RFIF & RFIF_IM_CCA) {
		NOP();
	}

	// SFD
	if (RFIF & RFIF_IM_SFD) {
		NOP();
	}
}