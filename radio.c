#include "radio.h"

// Generate data buffers
__xdata static uint8_t radio_rx_buffer[RADIO_MAX_PACKET_SIZE] = {0};
__xdata static uint8_t radio_tx_buffer[RADIO_MAX_PACKET_SIZE] = {0};

// Initialize data buffer sizes
static uint8_t radio_rx_buffer_size = 0;
static uint8_t radio_tx_buffer_size = 0;

// Initialize packet count
static uint8_t radio_n_packets = 0;

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_INIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_init(void) {

    // Power radio
    radio_power();

    // Configure radio
    radio_configure();

    // Enable radio interrupts
    radio_enable_interrupts();
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_POWER
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_power(void) {
    NOP();
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_ENABLE_INTERRUPTS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_enable_interrupts(void) {

    // Enable various RF interrupts
    RFIM = RFIM_IM_TXUNF | RFIM_IM_RXOVF | RFIM_IM_TIMEOUT | RFIM_IM_DONE |
           RFIM_IM_CS | RFIM_IM_PQT | RFIM_IM_CCA | RFIM_IM_SFD;

    // Enable RF interrupts
    RFTXRXIE = 1;

    // Enable interrupts
    IEN2 |= IEN2_RFIE;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_STATE_IDLE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_state_idle(void) {

    // Go in idle state
    RFST = RFST_SIDLE;

    // Wait until radio is in idle state
    while (RF_MARCSTATE != RF_MARCSTATE_IDLE) {
        NOP();
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_STATE_RECEIVE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_state_receive(void) {

    // Go in receive mode
    RFST = RFST_SRX;

    // Wait until radio is in receive state
    while (RF_MARCSTATE != RF_MARCSTATE_RX) {
        NOP();
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_STATE_TRANSMIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_state_transmit(void) {

    // Go in receive mode
    RFST = RFST_STX;

    // Wait until radio is in receive state
    while (RF_MARCSTATE != RF_MARCSTATE_TX) {
        NOP();
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_CONFIGURE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_configure(void) {

    // Configure radio
    SYNC1 =     0xFF;
    SYNC0 =     0x00;
    PKTLEN =    0xFF;
    PKTCTRL1 =  0x00;
    PKTCTRL0 =  0x00;
    ADDR =      0x00;
    FSCTRL1 =   0x06;
    FSCTRL0 =   0x00;
    MDMCFG4 =   0x99;
    MDMCFG3 =   0x66;
    MDMCFG2 =   0x33;
    MDMCFG1 =   0x61;
    MDMCFG0 =   0x7E;
    DEVIATN =   0x15;
    MCSM2 =     0x07;
    MCSM1 =     0x30;
    MCSM0 =     0x18;
    FOCCFG =    0x17;
    FREND1 =    0xB6;
    FREND0 =    0x11;
    FSCAL3 =    0xE9;
    FSCAL2 =    0x2A;
    FSCAL1 =    0x00;
    FSCAL0 =    0x1F;
    TEST1 =     0x31;
    TEST0 =     0x09;
    PA_TABLE0 = 0x00;
    AGCCTRL2 =  0x07;
    AGCCTRL1 =  0x00;
    AGCCTRL0 =  0x91;

    // Radio locale
    // North America (NA)
    #if RADIO_LOCALE == RADIO_LOCALE_NA
        FREQ2 =     0x26;
        FREQ1 =     0x30;
        FREQ0 =     0x70;
        CHANNR =    0x02;
        PA_TABLE1 = 0xC0;
    // Worldwide (WW)
    #elif RADIO_LOCALE == RADIO_LOCALE_WW
        FREQ2 =     0x24;
        FREQ1 =     0x2E;
        FREQ0 =     0x38;
        CHANNR =    0x00;
        PA_TABLE1 = 0xC2;
    #endif
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_RECEIVE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
uint8_t radio_receive(uint32_t timeout) {

    // Initialize read byte count, received byte, and flag to return
    uint8_t n = 0;
    uint8_t byte = 0;
    uint8_t flag = 0;

    // Reset buffer size
    radio_rx_buffer_size = 0;

    // Reset timer counter
    timer_counter_reset();

    // Put radio in idle state
    radio_state_idle();

    // Put radio in receive state
    radio_state_receive();

    // Loop in parallel of RF ISRs and react when new bytes are received
    while (1) {

        // If new unread byte(s)
        if (radio_rx_buffer_size > n) {

            // Get new byte
            byte = radio_tx_buffer[n];

            // Queue it for USB transfer
            usb_queue_byte(byte);

            // Check for absence of data
            if (n == 2 && byte == 0) {

                // Assign no data flag
                flag = RADIO_ERROR_NO_DATA;

                // Exit
                break;
            }

            // If end of packet
            if (n > 2 && n == radio_rx_buffer_size && byte == 0) {

                // Exit
                break;
            }

            // Update read byte count
            n++;
        }

        // If no bytes received
        else if (radio_rx_buffer_size == 0) {

            // If timeout given and expired
            if (timeout > 0 && timer_counter > timeout) {

                // Assign timeout flag
                flag = RADIO_ERROR_TIMEOUT;

                // Exit
                break;
            }
        }
    }

    // Put radio in idle state
    radio_state_idle();

    // If data successfully received
    if (flag == 0) {

        // Send packet over USB
        usb_send_bytes_bulk();
    }

    // Otherwise
    else {

        // Switch LED
        led_switch();
    }

    // Return info flag
    return flag;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_TRANSMIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
uint8_t radio_transmit(void) {

    // Put radio in idle state
    radio_state_idle();

    // Put radio in transmit state
    radio_state_transmit();

    // Return info flag
    return 0;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_RFTXRX_ISR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_rftxrx_isr(void) __interrupt RFTXRX_VECTOR {

    // Define byte to read/write
    uint8_t byte = 0;

    // Check MARC state
    switch (RF_MARCSTATE) {

        // Receiving
        case RF_MARCSTATE_RX:

            // Read byte from radio
            byte = RFD;

            // New packet
            if (radio_rx_buffer_size == 0) {

                // First byte: packet count
                radio_rx_buffer[0] = radio_n_packets;

                // Second byte: received signal strength indication (RSSI)
                radio_rx_buffer[1] = RSSI;

                // Update buffer size
                radio_rx_buffer_size = 2;

                // Update packet count
                radio_n_packets++;
            }

            // Packet incomplete
            if (radio_rx_buffer_size < RADIO_MAX_PACKET_SIZE) {

                // Fill buffer and update its size
                radio_rx_buffer[radio_rx_buffer_size++] = byte;
            }

            // Overflow
            else {
                NOP();
            }

            // Exit
            break;

        // Transmitting
        case RF_MARCSTATE_TX:

            // Write byte to radio
            RFD = byte;

            // Exit
            break;
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_GENERAL_ISR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_general_isr(void) __interrupt RF_VECTOR {

    // TX underflow
    if (RFIF & RFIF_IM_TXUNF) {

        // Enter IDLE state
        RFST = RFST_SIDLE;

        // Reset interrupt flag
        RFIF &= ~RFIF_IM_TXUNF;
    }

    // RX overflow
    if (RFIF & RFIF_IM_RXOVF) {

        // Enter IDLE state
        RFST = RFST_SIDLE;

        // Reset interrupt flag
        RFIF &= ~RFIF_IM_RXOVF;
    }

    // RX timeout
    if (RFIF & RFIF_IM_TIMEOUT) {

        // Reset interrupt flag
        RFIF &= ~RFIF_IM_TIMEOUT;
    }

    // Packet received/transmitted
    if (RFIF & RFIF_IM_DONE) {

        // Reset interrupt flag
        RFIF &= ~RFIF_IM_DONE;
    }

    // CS
    if (RFIF & RFIF_IM_CS) {

        // Reset interrupt flag
        RFIF &= ~RFIF_IM_CS;
    }

    // PQT reached
    if (RFIF & RFIF_IM_PQT) {

        // Reset interrupt flag
        RFIF &= ~RFIF_IM_PQT;
    }

    // CCA
    if (RFIF & RFIF_IM_CCA) {

        // Reset interrupt flag
        RFIF &= ~RFIF_IM_CCA;
    }

    // SFD
    if (RFIF & RFIF_IM_SFD) {

        // Reset interrupt flag
        RFIF &= ~RFIF_IM_SFD;
    }

    // Reset CPU interrupt flags
    S1CON = 0;
}