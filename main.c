#include "main.h"

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    MAIN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void main(void) {

    // Initialize stuff
    clock_init();
    timer_init();
    led_init();
    usb_init();
    radio_init();

    // Enable interrupts
    interrupts_enable();

    // Start timer
    timer_start();

    // Loop
    while (1) {

        // Wait for commands
        command_get();
    }
}