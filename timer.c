#include "timer.h"

#define F_CPU    375 // (kHz)
#define PRESCALE 8   // (-)
#define PERIOD   400 // (ms)
#define N        (F_CPU / PRESCALE * PERIOD) // (-) MAX: 65536

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

    // Enable overflow interrupts
    //OVFIM = 1;

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

    // Reset interrupt flag
    T1CTL &= ~T1CTL_CH0IF;

    // Update compare value (leapfrogging)
    T1CC0L += getByte(N, 0);
    T1CC0H += getByte(N, 1);

    // Switch LED
    led_switch();
}