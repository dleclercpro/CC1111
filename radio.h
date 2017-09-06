#ifndef _RADIO_H_
#define _RADIO_H_

void radio_init(void);
void radio_power(void);
void radio_enable_interrupts(void);
void radio_rftxrx_isr(void) __interrupt RFTXRX_VECTOR;
void radio_general_isr(void) __interrupt RF_VECTOR;