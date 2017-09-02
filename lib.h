#ifndef _LIB_H_
#define _LIB_H_

#include <stdint.h>

#define NOP() __asm nop __endasm // SDCC compiler ASM indications

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	SET_WORD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	Store 2 bytes in a pair of registers
*/
#define set_word(name, bytes)     \
	do {				          \
		name##L = ((uint16_t)(bytes)) & 0xFF; \
		name##H = ((uint16_t)(bytes)) >> 8;   \
	} while (0)

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	GET_WORD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	Read 2 bytes in a pair of registers
*/
#define get_word(name) ((uint16_t)(name##L)) + (((uint16_t)(name##H)) << 8)

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	LE_WORD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	Return word in little endian fashion, with both bytes separated by a comma
*/
#define le_word(bytes) (((uint16_t)(bytes)) & 255, ((uint16_t)(bytes)) >> 8)

#endif