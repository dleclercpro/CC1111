#ifndef _TIMER_H_
#define _TIMER_H_

#include "cc1111.h"
#include "led.h"
#include "lib.h"

void timer_init(void);
void timer_start(void);
void timer_isr(void) __interrupt T1_VECTOR;

#endif