#ifndef _RADIO_H_
#define _RADIO_H_

// Radio states
#define RADIO_STATE_IDLE        0
#define RADIO_STATE_TRANSMIT    1
#define RADIO_STATE_RECEIVE     2
#define RADIO_STATE_CALIBRATION 3
#define RADIO_STATE_RX_OVERFLOW 4
#define RADIO_STATE_TX_OVERFLOW 5

// Radio locale
#define RADIO_LOCALE_NA 0
#define RADIO_LOCALE_WW 1
#define RADIO_LOCALE    RADIO_LOCALE_NA

void radio_init(void);
void radio_power(void);
void radio_enable_interrupts(void);
void radio_configure(void);
void radio_rftxrx_isr(void) __interrupt RFTXRX_VECTOR;
void radio_general_isr(void) __interrupt RF_VECTOR;

#endif