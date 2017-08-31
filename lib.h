#ifndef _LIB_H_
#define _LIB_H_

#include <stdint.h>

#define NOP() __asm nop __endasm // SDCC compiler ASM indications

uint8_t getByte(uint16_t bytes, uint8_t n);

#endif