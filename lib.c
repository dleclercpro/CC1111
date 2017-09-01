#include "lib.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	SET_WORD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	Store 2 bytes in a pair of registers
*/
#define set_word(name, bytes)    \
	do {				         \
		name##L = (bytes) & 255; \
		name##H = (bytes) >> 8;  \
	} while(0)

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	LE_WORD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	Return word in little endian fashion, with both bytes separated by a comma
*/
#define le_word(bytes) ((bytes) & 255, (bytes) >> 8)

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	GET_BYTE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	Note: can only split 2 bytes due to CPU program memory.
*/
uint8_t get_byte(uint16_t bytes, uint8_t n) {
	return (bytes & (255 << (n * 8))) >> (n * 8);
}