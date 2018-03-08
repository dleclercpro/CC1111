#include "radio.h"

// Generate data buffers
__xdata static uint8_t radio_rx_buffer[RADIO_MAX_PACKET_SIZE] = {0};
__xdata static uint8_t radio_tx_buffer[RADIO_MAX_PACKET_SIZE] = {0};

// Initialize data buffer sizes
static uint8_t radio_rx_buffer_size = 0;
static uint8_t radio_tx_buffer_size = 0;

// Initialize data buffer index
static uint8_t radio_tx_buffer_index = 0;

// Initialize writing underflow count
static uint8_t radio_tx_underflow_count = 0;

// Initialize packet count
static uint8_t radio_packet_count = 0;

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_INIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_init(void) {

    // Configure radio
    radio_configure();

    // Enable radio interrupts
    radio_enable_interrupts();
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
    RADIO_STATE_WAIT_IDLE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_state_wait_idle(void) {

    // Wait until radio is in idle state
    while (RF_MARCSTATE != RF_MARCSTATE_IDLE) {
        NOP();
    }
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
    radio_state_wait_idle();
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_STATE_RECEIVE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_state_receive(void) {

    // Go in receive mode
    RFST = RFST_SRX;

    // Wait until radio is in receive mode
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

    // Go in transmit mode
    RFST = RFST_STX;

    // Wait until radio is in transmit mode
    while (RF_MARCSTATE != RF_MARCSTATE_TX) {
        NOP();
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_CONFIGURE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Configuration of radio.

    Reference frequency: F = 24 MHz

    Base frequency: f = F / 2**16 * (FREQ2 << 8*2 + FREQ1 << 8*1 + FREQ0 << 8*0)
    Resolution: 0.366 kHz
    
    Channel bandwidth: df = F / 2**18 * (256 + MDMCFG0) * 2**(MDMCFG1 & 0x03)
    Resolution: 23.438 kHz
    
    Effective frequency: f' = f + df
*/
void radio_configure(void) {

    // Configure radio
    SYNC1     = 0xFF;
    SYNC0     = 0x00;
    PKTLEN    = 0xFF;
    PKTCTRL1  = 0x00;
    PKTCTRL0  = 0x00;
    ADDR      = 0x00;
    FSCTRL1   = 0x06;
    FSCTRL0   = 0x00;
    MDMCFG4   = 0x99;
    MDMCFG3   = 0x66;
    MDMCFG2   = 0x33;
    MDMCFG1   = 0x61;
    MDMCFG0   = 0x7E; // Channel bandwidth: 69.946 kHz
    DEVIATN   = 0x15;
    MCSM2     = 0x07;
    MCSM1     = 0x30;
    MCSM0     = 0x18;
    FOCCFG    = 0x17;
    FREND1    = 0xB6;
    FREND0    = 0x11;
    FSCAL3    = 0xE9;
    FSCAL2    = 0x2A;
    FSCAL1    = 0x00;
    FSCAL0    = 0x1F;
    TEST1     = 0x31;
    TEST0     = 0x09;
    PA_TABLE0 = 0x00;
    AGCCTRL2  = 0x07;
    AGCCTRL1  = 0x00;
    AGCCTRL0  = 0x91;

    // Radio locale
    // North America (NA)
    // Base frequency: f = 916.541 MHz
    // Effective frequency: f' = 916.681 MHz
    #if RADIO_LOCALE == RADIO_LOCALE_NA
        FREQ2     = 0x26;
        FREQ1     = 0x30;
        FREQ0     = 0x70;
        CHANNR    = 0x02;
        PA_TABLE1 = 0xC0;

    // Worldwide (WW)
    // Base frequency: f = 868.333 MHz
    // Effective frequency: f' = 868.333 MHz
    #elif RADIO_LOCALE == RADIO_LOCALE_WW
        FREQ2     = 0x24;
        FREQ1     = 0x2E;
        FREQ0     = 0x38;
        CHANNR    = 0x00;
        PA_TABLE1 = 0xC2;
    #endif
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_REGISTER
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
uint8_t * radio_register(uint8_t addr) {

    // Initialize register pointer
    uint8_t *reg = 0;

    // Assign pointer
    switch (addr) {
        case 0:
            reg = &SYNC1;
            break;
        case 1:
            reg = &SYNC0;
            break;
        case 2:
            reg = &PKTLEN;
            break;
        case 3:
            reg = &PKTCTRL1;
            break;
        case 4:
            reg = &PKTCTRL0;
            break;
        case 5:
            reg = &ADDR;
            break;
        case 6:
            reg = &FSCTRL1;
            break;
        case 7:
            reg = &FSCTRL0;
            break;
        case 8:
            reg = &MDMCFG4;
            break;
        case 9:
            reg = &MDMCFG3;
            break;
        case 10:
            reg = &MDMCFG2;
            break;
        case 11:
            reg = &MDMCFG1;
            break;
        case 12:
            reg = &MDMCFG0;
            break;
        case 13:
            reg = &DEVIATN;
            break;
        case 14:
            reg = &MCSM2;
            break;
        case 15:
            reg = &MCSM1;
            break;
        case 16:
            reg = &MCSM0;
            break;
        case 17:
            reg = &BSCFG;
            break;
        case 18:
            reg = &FOCCFG;
            break;
        case 19:
            reg = &FREND1;
            break;
        case 20:
            reg = &FREND0;
            break;
        case 21:
            reg = &FSCAL3;
            break;
        case 22:
            reg = &FSCAL2;
            break;
        case 23:
            reg = &FSCAL1;
            break;
        case 24:
            reg = &FSCAL0;
            break;
        case 25:
            reg = &TEST1;
            break;
        case 26:
            reg = &TEST0;
            break;
        case 27:
            reg = &PA_TABLE1;
            break;
        case 28:
            reg = &PA_TABLE0;
            break;
        case 29:
            reg = &AGCCTRL2;
            break;
        case 30:
            reg = &AGCCTRL1;
            break;
        case 31:
            reg = &AGCCTRL0;
            break;
        case 32:
            reg = &FREQ2;
            break;
        case 33:
            reg = &FREQ1;
            break;
        case 34:
            reg = &FREQ0;
            break;
        case 35:
            reg = &CHANNR;
            break;
    }

    // Return register pointer
    return reg;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_RECEIVE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Timeout input given in s.
*/
void radio_receive(uint8_t channel, uint32_t timeout) {

    // Initialize byte count, current byte, and error
    uint8_t n = 0;
    uint8_t byte = 0;
    uint8_t error = 0;

    // Convert timeout from s to ms
    timeout *= 1000;

    // Reset timer counter
    timer_counter_reset();

    // Put radio in idle state
    radio_state_idle();

    // Set channel
    CHANNR = channel;

    // Reset buffer size
    radio_rx_buffer_size = 0;

    // Put radio in receive state
    radio_state_receive();

    // Loop parallel to RF ISRs and react when new bytes are received
    while (1) {

        // If new unread byte(s)
        if (radio_rx_buffer_size > n) {

            // Check for absence of data
            if (n == 0 && radio_rx_buffer_size > 2 && radio_rx_buffer[2] == 0) {

                // Assign no data error
                error = RADIO_ERROR_NO_DATA;

                // Exit
                break;
            }

            // Read current byte
            byte = radio_rx_buffer[n];

            // Update byte count
            n++;

            // If end of packet
            if (n > 2 && n == radio_rx_buffer_size && byte == 0) {

                // Exit
                break;
            }
        }

        // If no bytes received
        else if (radio_rx_buffer_size == 0) {

            // If timeout given and expired
            if (timeout > 0 && timer_counter > timeout) {

                // Assign timeout error
                error = RADIO_ERROR_TIMEOUT;

                // Exit
                break;
            }
        }
    }

    // Put radio back in idle state
    radio_state_idle();

    // If no error
    if (error == 0) {

        // Send bytes to master
        usb_tx_bytes(radio_rx_buffer);
    }

    // Otherwise
    else {

        // Send error to master
        usb_tx_byte(error);
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_SEND
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void radio_send(uint8_t channel, uint8_t repeat, uint32_t delay) {

    // Initialize byte to send
    uint8_t byte = 0;

    // Reset buffer size and index as well as underflow count
    radio_tx_buffer_size = 0;
    radio_tx_buffer_index = 0;
    radio_tx_underflow_count = 0;

    // Convert delay from s to ms
    delay *= 1000;

    // Put radio in idle state
    radio_state_idle();

    // Set channel
    CHANNR = channel;

    // Fill buffer
    while (1) {

        // If byte is not exceeding max packet length
        if (radio_tx_buffer_size <= RADIO_MAX_PACKET_SIZE) {

            // Get byte
            byte = usb_get_byte();
        }

        // Overflow
        else {

            // End byte
            byte = 0;
        }

        // Write byte in buffer and update its size
        radio_tx_buffer[radio_tx_buffer_size++] = byte;

        // If end-of-packet byte
        if (byte == 0) {

            // Exit
            break;
        }

    }

    // Put radio in transmit state
    radio_state_transmit();

    // Wait until packet is transmitted
    radio_state_wait_idle();

    // If repeat
    while (repeat--) {

        // If delay
        if (delay > 0) {

            // Reset timer counter
            timer_counter_reset();

            // Delay
            while (timer_counter < delay) {
                NOP();
            }
        }

        // Reset buffer index and underflow count
        radio_tx_buffer_index = 0;
        radio_tx_underflow_count = 0;

        // Put radio in transmit state
        radio_state_transmit();

        // Wait until packet is transmitted
        radio_state_wait_idle();
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RADIO_RFTXRX_ISR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ISRs either when a new byte is ready to be read from RFD (RX) or when a new
    one can be written to it (TX).
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

                // New packet: update count and avoid end-of-packet due to byte
                // overflow
                radio_packet_count = max(radio_packet_count + 1, 1);

                // First byte: packet count
                radio_rx_buffer[0] = radio_packet_count;

                // Second byte: received signal strength indication (RSSI)
                // Minimum set to 1 to avoid end-of-packet zero
                radio_rx_buffer[1] = max(RF_RSSI, 1);

                // Update buffer size
                radio_rx_buffer_size = 2;
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

            // If new byte is ready to be sent
            if (radio_tx_buffer_size > radio_tx_buffer_index) {

                // Get byte and update index
                byte = radio_tx_buffer[radio_tx_buffer_index++];

                // Give to radio
                RFD = byte;
            }

            // Otherwise: underflow
            else {

                // Tell radio no more bytes to send
                RFD = 0;

                // Update underflow count
                radio_tx_underflow_count++;

                // If underflow twice, radio should have sent all bytes
                if (radio_tx_underflow_count == 2) {

                    // Put radio back in idle state
                    radio_state_idle();
                }
            }

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