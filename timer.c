#include "timer.h"

// Preprocessor cannot deal with floating points!

#define TICKSPEED 24000000 // (Hz)
#define PRESCALE  32       // (-)
#define DELAY     1        // (ms)
#define N         (TICKSPEED / PRESCALE * DELAY / 1000) // (-) MAX: 65536

// Define counter (ms)
volatile uint32_t timer_counter = 0;

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
    SET_WORD(T1CC0, N - 1);

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
    T1CTL = T1CTL_MODE_FREE | T1CTL_DIV_32;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    TIMER_COUNTER_RESET
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void timer_counter_reset(void) {

    // Reset counter
    timer_counter = 0;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    TIMER_WAIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Wait for given delay (ms).
*/
void timer_wait(uint32_t delay) {

    // Reset timer counter
    timer_counter_reset();

    // Delay
    while (timer_counter < delay) {
        NOP();
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    TIMER_ISR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Note: CPU interrupt flag automatically cleared by hardware on ISR entry.
*/
void timer_isr(void) __interrupt T1_VECTOR {

    // Read current compare value and update it (leapfrogging)
    SET_WORD(T1CC0, GET_WORD(T1CC0) + N);

    // Update counter
    timer_counter++;

    // Reset interrupt flag
    T1CTL &= ~T1CTL_CH0IF;
}