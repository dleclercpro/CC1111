#include "timer.h"

#define TICKSPD  12000000 // (Hz)
#define PRESCALE 128      // (-)
#define DELAY    100      // (ms)
#define N        (TICKSPD / PRESCALE * DELAY / 1000) // (-) MAX: 65536

// Preprocessor cannot deal with floating points!

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    TIMER_INIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void timer_init(void) {

    // Suspend timer 1
    T1CTL = 0;

    // Reset its count
    T1CNTL = 0;

    // Configure channels
    T1CCTL0 = T1CCTL_MODE_COMPARE | T1CCTL_IM_ENABLED;
    T1CCTL1 = 0;
    T1CCTL2 = 0;

    // Define compare value
    T1CC0L = getByte(N - 1, 0);
    T1CC0H = getByte(N - 1, 1);

    // Disable overflow interrupt requests
    OVFIM = 0;

    // Enable interrupts
    T1IE = 1;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    TIMER_START
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void timer_start(void) {

    // Start timer in free mode with prescale divider
    T1CTL = T1CTL_MODE_FREE | T1CTL_DIV_128;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    TIMER_ISR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Note: CPU interrupt flag automatically cleared by hardware on ISR entry.
*/
void timer_isr(void) __interrupt T1_VECTOR {

    // Read current compare value
    uint16_t n = (T1CC0L << 0) + (T1CC0H << 8);

    // Update it (leapfrogging)
    n += N;

    // Set it
    T1CC0L = getByte(n, 0);
    T1CC0H = getByte(n, 1);

    // Switch LED
    led_switch();

    // Reset interrupt flag
    T1CTL &= ~T1CTL_CH0IF;
}