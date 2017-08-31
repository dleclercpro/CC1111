#include "timer.h"

#define F_CPU    24  // (MHz)
#define PRESCALE 128 // (-)
#define PERIOD   250 // (ms)
#define N        ((F_CPU / PRESCALE * PERIOD) * 1000) // (-)

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    TIMER_INIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Note: always read T1CNTL before T1CNTH!
*/
void timer_init(void) {

    // Suspend timer 1
    T1CTL = 0;

    // Reset its count
    T1CNTL = 0;

    // Define compare value
    // FIXME
    T1CC0L = (N - 1) & (0x0F << 0);
    T1CC0H = (N - 1) & (0x0F << 4);

    // Resume it in free mode with prescale divider
    T1CTL = T1CTL_MODE_FREE | T1CTL_DIV_128;
}