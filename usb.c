#include "usb.h"

// Generate instance of USB device
static struct usb_device usb_device;

// Generate instance of USB setup
static struct usb_setup_packet usb_setup_packet;

// Generate instance of USB byte counters
static struct usb_n_bytes usb_n_bytes;

// Generate data pointers
static uint8_t *usb_data_in;
static uint8_t *usb_data_out;

// Generate data buffer
__xdata static uint8_t usb_data_buffer[64];

// Initialize interrupt flags
volatile static uint8_t usb_if_in = 0;
volatile static uint8_t usb_if_out = 0;

// Initialize EP0 state
static uint8_t usb_ep0_state = USB_STATE_IDLE;

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_INIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_init(void) {

    // Enable USB
    usb_enable();

    // Start USB
    usb_on();

    // Set configuration
    usb_set_configuration(0);

    // Enable interrupts
    usb_enable_interrupts();

    // Reset interrupts
    usb_reset_interrupts();
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_ENABLE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_enable(void) {

    // Enable USB
    P1DIR |= 1;
    P1_0 = 1;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_ON
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_on(void) {

    // Power up controller
    SLEEP |= SLEEP_USB_EN;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_OFF
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_off(void) {

    // Power down controller
    SLEEP &= ~SLEEP_USB_EN;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_STALL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_stall(void) {

    // Send stall packet
    USBCS0 |= USBCS0_SEND_STALL;

    // Reset all EPs
    usb_reset_ep(-1);
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_RESET_FLAGS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_reset_flags(void) {

    // Reset interrupt flags
    usb_if_in = 0;
    usb_if_out = 0;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_RESET_EP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_reset_ep(int ep) {

    // Reset counters
    usb_reset_counters(ep);

    // EP0
    if (ep == USB_EP_CONTROL) {

        // Reset state
        usb_ep0_state = USB_STATE_IDLE;
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_RESET_COUNTERS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_reset_counters(int ep) {

    // EP
    switch (ep) {

        // EP0
        case USB_EP_CONTROL:

            // Reset byte counters
            usb_n_bytes.ep0_out = 0;
            usb_n_bytes.ep0_in = 0;
            break;

        // EP OUT
        case USB_EP_OUT:

            // Reset byte counter
            usb_n_bytes.ep_out = 0;
            break;

        // EP IN
        case USB_EP_IN:

            // Reset byte counters
            usb_n_bytes.ep_in = 0;
            usb_n_bytes.ep_in_last = 0;
            break;

        // Default: all EPs
        default:

            // Reset byte counters
            usb_n_bytes.ep0_out = 0;
            usb_n_bytes.ep0_in = 0;
            usb_n_bytes.ep_out = 0;
            usb_n_bytes.ep_in = 0;
            usb_n_bytes.ep_in_last = 0;
            break;
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_ENABLE_INTERRUPTS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_enable_interrupts(void) {

    // Enable control and IN EP interrupts
    USBIIE = USB_EP0IE | USB_INEP5IE;

    // Enable OUT EP interrupts
    USBOIE = USB_OUTEP4IE;

    // Enable reset interrupts
    USBCIE = USBCIE_RSTIE;

    // Enable interrupts
    IEN2 |= IEN2_USBIE;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_RESET_INTERRUPTS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_reset_interrupts(void) {

    // Reset any pending interrupts
    USBCIF = 0;
    USBIIF = 0;
    USBOIF = 0;

    // Re-enable interrupts
    USBIF = 0;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_SET_EP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Note: EP range given by [0, 5].
*/
void usb_set_ep(uint8_t ep) {

    // Set EP
    USBINDEX = ep;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_GET_EP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
uint8_t usb_get_ep(void) {

    // Get EP
    return USBINDEX;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_WRITE_BYTE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_write_byte(uint8_t byte) {

    // Set byte to active EP FIFO
    USBFIFO[usb_get_ep() << 1] = byte;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_READ_BYTE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
uint8_t usb_read_byte(void) {

    // Read and return byte from active EP FIFO
    return USBFIFO[usb_get_ep() << 1];
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_EP0_QUEUE_BYTE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_ep0_queue_byte(uint8_t byte) {

    // Queue byte in buffer
    usb_data_buffer[usb_n_bytes.ep0_in++] = byte;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_EP0_WRITE_BYTES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_ep0_write_bytes(uint8_t n) {

    // Loop on bytes
    while (n--) {

        // Write byte
        usb_write_byte(*usb_data_in++);
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_EP0_READ_BYTES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_ep0_read_bytes(uint8_t n) {

    // Loop on bytes
    while (n--) {

        // Read byte
        *usb_data_out++ = usb_read_byte();
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_EP0_SEND_BYTES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_ep0_send_bytes(void) {

    // Initialize number of bytes to send
    uint8_t n = min(usb_n_bytes.ep0_in, USB_SIZE_EP_CONTROL);

    // Write bytes
    usb_ep0_write_bytes(n);

    // Bytes ready
    USBCS0 |= USBCS0_INPKT_RDY;

    // Update expected number of bytes remaining
    usb_n_bytes.ep0_in -= n;

    // If last packet sent
    if (n < USB_SIZE_EP_CONTROL) {

        // End of data
        USBCS0 |= USBCS0_DATA_END;

        // Update EP state
        usb_ep0_state = USB_STATE_IDLE;
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_EP0_RECEIVE_BYTES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_ep0_receive_bytes(uint8_t end) {

    // Get number of bytes to receive
    uint8_t n = min(min(usb_n_bytes.ep0_out, USBCNT0), USB_SIZE_EP_CONTROL);

    // Read bytes
    usb_ep0_read_bytes(n);

    // Byte read
    USBCS0 |= USBCS0_CLR_OUTPKT_RDY;

    // Update expected number of bytes remaining
    usb_n_bytes.ep0_out -= n;

    // If last packet read
    if (usb_n_bytes.ep0_out == 0) {

        // If EOD signaling allowed
        if (end) {

            // End of data
            USBCS0 |= USBCS0_DATA_END;
        }

        // Update EP state
        usb_ep0_state = USB_STATE_IDLE;
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_SEND_BYTES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_send_bytes(void) {

    // Select EP
    usb_set_ep(USB_EP_IN);

    // Data in FIFO is ready
    USBCSIL |= USBCSIL_INPKT_RDY;

    // Store number of bytes sent
    usb_n_bytes.ep_in_last = usb_n_bytes.ep_in;

    // No more bytes to send
    usb_n_bytes.ep_in = 0;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_RECEIVED_BYTES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_received_bytes(void) {

    // Select EP
    usb_set_ep(USB_EP_OUT);

    // Packet fully read from FIFO
    USBCSOL &= ~USBCSOL_OUTPKT_RDY;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_WAIT_IN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_wait_in(void) {

    // Select EP
    usb_set_ep(USB_EP_IN);

    // Wait until new data can be written to FIFO
    while (USBCSIL & USBCSIL_INPKT_RDY) {
        NOP();
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_PUT_BYTE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_put_byte(uint8_t byte) {

    // Wait until FIFO is ready
    usb_wait_in();

    // Write byte
    usb_write_byte(byte);

    // If FIFO is full
    if (++usb_n_bytes.ep_in == USB_SIZE_EP_IN) {

        // Send bytes
        usb_send_bytes();
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_PUT_BYTES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_put_bytes(uint8_t *bytes) {

    // Write byte until last byte is reached
    while (bytes[0] != 0) {

        // Put current byte
        usb_put_byte(bytes[0]);

        // Update pointer
        bytes++;
    }

    // Flush bytes
    usb_flush_bytes();
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_FLUSH_BYTES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_flush_bytes(void) {

    // If bytes remaining or last packet was full
    if (usb_n_bytes.ep_in || usb_n_bytes.ep_in_last == USB_SIZE_EP_IN) {

        // Wait until FIFO is ready
        usb_wait_in();

        // Send bytes
        usb_send_bytes();
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_POLL_BYTE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
int usb_poll_byte(void) {

    // Initialize byte to poll
    uint8_t byte;

    // If first byte
    if (usb_n_bytes.ep_out == 0) {

        // Select EP
        usb_set_ep(USB_EP_OUT);

        // If packet not ready
        if ((USBCSOL & USBCSOL_OUTPKT_RDY) == 0) {

            // Keep trying
            return -1;
        }

        // Update byte count
        usb_n_bytes.ep_out = USBCNTL | ((USBCNTH & 7) << 8);

        // If still no byte to read
        if (usb_n_bytes.ep_out == 0) {

            // Received bytes
            usb_received_bytes();

            // Keep trying
            return -1;
        }
    }

    // Read byte from FIFO
    byte = usb_read_byte();

    // If no more bytes to read
    if (--usb_n_bytes.ep_out == 0) {

        // Received bytes
        usb_received_bytes();
    }

    // Return polled byte
    return byte;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_GET_BYTE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
uint8_t usb_get_byte(void) {

    // Initialize byte
    int byte;

    // Poll it
    while ((byte = usb_poll_byte()) == -1) {
        NOP();
    }

    // Return it
    return (uint8_t) byte;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_SET_ADDRESS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Note: address given by bits [0, 6].
*/
void usb_set_address(uint8_t addr) {

    // Set address
    USBADDR = addr;

    // Wait until address is set
    while (USBADDR != addr) {
        NOP();
    }

    // Test LED
    led_switch();
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_SET_CONFIGURATION
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Note: maximum packet size must be given in units of 8 bytes
*/
void usb_set_configuration(uint8_t value) {

    // Update device configuration (only one)
    usb_device.configuration = value;

    // Set maximum packet sizes
    usb_set_ep(USB_EP_OUT);
    USBMAXI = 0;
    USBMAXO = USB_SIZE_EP_OUT / 8;

    // Set maximum packet sizes
    usb_set_ep(USB_EP_IN);
    USBMAXI = USB_SIZE_EP_IN / 8;
    USBMAXO = 0;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_GET_CONFIGURATION
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_get_configuration(void) {

    // Queue configuration
    usb_ep0_queue_byte(usb_device.configuration);
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_GET_DESCRIPTOR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_get_descriptor(uint16_t value) {

    // Get type and index
    uint8_t type = value >> 8;
    uint8_t index = value & 255;

    // Initialize pointer to current descriptor
    uint8_t *descriptor = usb_descriptors;

    // Loop on descriptors
    while (descriptor[0] != 0) {

        // Compare types and decrease index until desired descriptor is matched
        if (descriptor[1] == type && index-- == 0) {

            // If asked for configuration descriptor
            if (type == USB_DESC_CONFIGURATION) {

                // Read descriptor length
                usb_n_bytes.ep0_in = descriptor[2];
            }

            // Otherwise
            else {

                // Read descriptor length
                usb_n_bytes.ep0_in = descriptor[0];
            }

            // Link data to descriptor
            usb_data_in = descriptor;

            // Exit
            return;
        }

        // Update pointer
        descriptor += descriptor[0];
    }

    // No descriptor found, terminate transaction
    usb_stall();
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_GET_SETUP_PACKET
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_get_setup_packet(void) {

    // Link data with USB setup
    usb_data_out = (uint8_t *) &usb_setup_packet;

    // Setup packet is always 8 bytes long
    usb_n_bytes.ep0_out = 8;

    // Read setup packet
    usb_ep0_receive_bytes(0);
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_PARSE_SETUP_PACKET
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_parse_setup_packet(void) {

    // If data stage
    if (usb_setup_packet.length) {

        // Determine direction of exchange
        switch (usb_setup_packet.info & USB_SETUP_DIRECTION) {

            // IN
            case (USB_DIRECTION_IN):

                // Link data with buffer
                usb_data_in = usb_data_buffer;
                
                // Update EP state
                usb_ep0_state = USB_STATE_SEND;
                break;

            // OUT
            case (USB_DIRECTION_OUT):

                // Link data with buffer
                usb_data_out = usb_data_buffer;

                // Set number of packets to receive
                usb_n_bytes.ep0_out = usb_setup_packet.length;

                // Update EP state
                usb_ep0_state = USB_STATE_RECEIVE;
                break;
        }
    }

    // Otherwise
    else {

        // End of data
        USBCS0 |= USBCS0_DATA_END;
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_SETUP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_setup(void) {

    // Get setup packet
    usb_get_setup_packet();

    // If incomplete setup packet
    if (usb_n_bytes.ep0_out != 0) {

        // Skip setup stage and wait for another setup packet from host
        return;
    }

    // Parse setup packet
    usb_parse_setup_packet();

    // Only respond to standard USB requests
    switch (usb_setup_packet.info & USB_SETUP_TYPE) {

        // Standard
        case USB_TYPE_STANDARD:

            // Recipient
            switch (usb_setup_packet.info & USB_SETUP_RECIPIENT) {

                // Device
                case USB_RECIPIENT_DEVICE:

                    // Request
                    switch (usb_setup_packet.request) {

                        case USB_REQUEST_GET_STATUS:
                            usb_ep0_queue_byte(0); // Device bus powered
                            usb_ep0_queue_byte(0); // Remote wake up disabled
                            break;

                        //case USB_REQUEST_CLEAR_FEATURE:
                        //    break;

                        //case USB_REQUEST_SET_FEATURE:
                        //    break;

                        case USB_REQUEST_SET_ADDRESS:
                            usb_set_address(usb_setup_packet.value);
                            break;

                        case USB_REQUEST_GET_DESCRIPTOR:
                            usb_get_descriptor(usb_setup_packet.value);
                            break;

                        //case USB_REQUEST_SET_DESCRIPTOR:
                        //    break;

                        case USB_REQUEST_GET_CONFIGURATION:
                            usb_get_configuration();
                            break;

                        case USB_REQUEST_SET_CONFIGURATION:
                            usb_set_configuration(usb_setup_packet.value);
                            break;
                    }

                    break;

                // Interface
                case USB_RECIPIENT_INTERFACE:

                    // Request
                    switch (usb_setup_packet.request) {

                        case USB_REQUEST_GET_STATUS:
                            usb_ep0_queue_byte(0); // Reserved for future use?
                            usb_ep0_queue_byte(0); // Reserved for future use?
                            break;

                        //case USB_REQUEST_CLEAR_FEATURE:
                        //    break;

                        //case USB_REQUEST_SET_FEATURE:
                        //    break;

                        case USB_REQUEST_GET_INTERFACE:
                            usb_ep0_queue_byte(0); // No alternative interfaces
                            break;

                        //case USB_REQUEST_SET_INTERFACE:
                        //    break;
                    }

                    break;

                // Endpoint
                case USB_RECIPIENT_EP:

                    // Request
                    switch (usb_setup_packet.request) {

                        case USB_REQUEST_GET_STATUS:
                            usb_ep0_queue_byte(0); // Not halted
                            usb_ep0_queue_byte(0); // Not stalled
                            break;

                        //case USB_REQUEST_CLEAR_FEATURE:
                        //    break;

                        //case USB_REQUEST_SET_FEATURE:
                        //    break;

                        //case USB_REQUEST_SYNCH_FRAME:
                        //    break;
                    }

                    break;
            }

            break;

        // Class
        //case USB_TYPE_CLASS:
        //    break;
    }

    // If data to send
    if (usb_ep0_state == USB_STATE_SEND) {

        // If number of bytes to send is larger than asked by host
        usb_n_bytes.ep0_in = min(usb_n_bytes.ep0_in, usb_setup_packet.length);

        // Send first bytes
        usb_ep0_send_bytes();
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_CONTROL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_control(void) {

    // Select control EP
    usb_set_ep(USB_EP_CONTROL);

    // Control transfer ends due to a premature end of control transfer or
    // EP receives an unexpected token during the data stage
    if (USBCS0 & USBCS0_SETUP_END) {

        // Reset flag
        USBCS0 |= USBCS0_CLR_SETUP_END;

        // Reset EP
        usb_reset_ep(USB_EP_CONTROL);
    }

    // EP is stalled
    if (USBCS0 & USBCS0_SENT_STALL) {

        // Reset flag
        USBCS0 &= ~USBCS0_SENT_STALL;

        // Reset EP
        usb_reset_ep(USB_EP_CONTROL);
    }

    // If packet requested
    if (usb_ep0_state == USB_STATE_SEND) {

        // Send data
        usb_ep0_send_bytes();
    }

    // If packet received
    if (USBCS0 & USBCS0_OUTPKT_RDY) {

        // EP0 state
        switch (usb_ep0_state) {

            // Transfer stage
            case (USB_STATE_RECEIVE):

                // Receive data
                usb_ep0_receive_bytes(1);
                break;

            // Idle
            case (USB_STATE_IDLE):

                // Setup stage
                usb_setup();
                break;
        }
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_OUT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_out(void) {

    // Select EP
    usb_set_ep(USB_EP_OUT);

    // EP is stalled
    if (USBCSOL & USBCSOL_SENT_STALL) {

        // Reset flag
        USBCSOL &= ~USBCSOL_SENT_STALL;

        // Reset EP
        usb_reset_ep(USB_EP_OUT);
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_IN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_in(void) {

    // Select EP
    usb_set_ep(USB_EP_IN);

    // EP is stalled
    if (USBCSIL & USBCSIL_SENT_STALL) {

        // Reset flag
        USBCSIL &= ~USBCSIL_SENT_STALL;

        // Reset EP
        usb_reset_ep(USB_EP_IN);
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB state machine
*/
void usb(void) {

    // Store current EP
    uint8_t ep = usb_get_ep();

    // If reset flag raised
    if (USBCIF & USBCIF_RSTIF) {

        // Re-enable interrupts
        usb_enable_interrupts();

        // Reset all EPs
        usb_reset_ep(-1);
    }

    // If control EP0 flag raised
    if (usb_if_in & USB_IF_CONTROL) {

        // Control sequence
        usb_control();
    }

    // If OUT EP4 flag raised
    if (usb_if_out & USB_IF_OUT) {

        // Data to device sequence
        usb_out();
    }

    // If IN EP5 flag raised
    if (usb_if_in & USB_IF_IN) {

        // Data to host sequence
        usb_in();
    }

    // Reset interrupt flags
    usb_reset_flags();

    // Restore last EP
    usb_set_ep(ep);
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_ISR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Warning: interrupts shared with port 2!
*/
void usb_isr(void) __interrupt P2INT_VECTOR {

    // Store interrupt flags (cleared upon reading)
    usb_if_in |= USBIIF;
    usb_if_out |= USBOIF;

    // Re-enable interrupts
    USBIF = 0;

    // Run USB state machine
    usb();
}