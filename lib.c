#include "lib.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	GETBYTE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	Note: can only split 2 bytes due to CPU program memory.
*/
uint8_t getByte(uint16_t bytes, uint8_t n) {
	return (bytes & (255 << (n * 8))) >> (n * 8);
}