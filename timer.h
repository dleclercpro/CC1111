#ifndef _TIMER_H_
#define _TIMER_H_

#include "cc1111.h"
#include "led.h"
#include "lib.h"

// Declare external variables
extern volatile uint32_t timer_counter;

void timer_init(void);
void timer_start(void);
void timer_counter_reset(void);
void timer_isr(void) __interrupt T1_VECTOR;

#endif