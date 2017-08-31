#include "timer.h"
#include "led.h"

#define F_CPU    24  // (MHz)
#define PRESCALE 128 // (-)
#define PERIOD   500 // (ms)
#define N        ((F_CPU / PRESCALE * PERIOD) * 1000) // (-)

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

    // Configure it in output compare mode
    T1CCTL0 |= T1CCTL_NO_CAPTURE | T1CCTL_MODE_COMPARE | T1CCTL_CMP_SET |
               T1CCTL_IM_ENABLED | T1CCTL_CPSEL_NORMAL;

    // Define compare value
    T1CC0L = (N - 1) >> 0;
    T1CC0H = (N - 1) >> 8;

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

    // Update compare value
    T1CC0L += N >> 0;
    T1CC0H += N >> 8;

    // Switch LED
    led_switch();
}