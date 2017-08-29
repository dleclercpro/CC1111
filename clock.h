#ifndef _CLOCK_H_
#define _CLOCK_H_

#include "cc1111.h"

#define NOP() __asm nop __endasm // SDCC compiler ASM indications

void clock_init();
void timer_init();

#endif