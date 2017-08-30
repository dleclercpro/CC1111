#ifndef _LIB_H_
#define _LIB_H_

#define NOP() __asm nop __endasm // SDCC compiler ASM indications

void delay(int t);

#endif