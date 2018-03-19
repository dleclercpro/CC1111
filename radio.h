#ifndef _RADIO_H_
#define _RADIO_H_

#include "cc1111.h"
#include "lib.h"
#include "timer.h"
#include "led.h"
#include "usb.h"

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

// Max packet size
#define RADIO_MAX_PACKET_SIZE 192

// Radio errors
#define RADIO_ERROR_TIMEOUT 0xAA
#define RADIO_ERROR_NO_DATA 0xBB

void radio_init(void);
void radio_enable_interrupts(void);
void radio_state_wait_idle(void);
void radio_state_idle(void);
void radio_state_receive(void);
void radio_state_transmit(void);
void radio_configure(void);
uint8_t * radio_register(uint8_t addr);
uint8_t radio_receive(uint8_t channel, uint32_t timeout);
void radio_send(uint8_t channel, uint8_t repeat, uint32_t delay);
void radio_resend(void);
void radio_rftxrx_isr(void) __interrupt RFTXRX_VECTOR;
void radio_general_isr(void) __interrupt RF_VECTOR;

#endif