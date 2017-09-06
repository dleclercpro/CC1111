#include "usb.h"

// Generate instance of USB device
static struct usb_device usb_device;

// Generate instance of USB setup
static struct usb_setup_packet usb_setup_packet;

// Generate data pointers
static uint8_t *usb_data_in = NULL;
static uint8_t *usb_data_out = NULL;

// Initialize control/configure register pointers
static uint8_t *usb_cc_in = NULL;
static uint8_t *usb_cc_out = NULL;

// Initialize interrupt flags
static uint8_t usb_if_in = 0;
static uint8_t usb_if_out = 0;
static uint8_t usb_if_eod = 0;

// Generate data buffer/queue
__xdata static uint8_t usb_data_queue[8] = {0};
__xdata static uint8_t usb_data_buffer[64] = {0};

// Initialize byte counts
static uint8_t usb_size = 0;
static uint8_t usb_n_bytes_in = 0;
static uint8_t usb_n_bytes_out = 0;

// Generate state
static uint8_t usb_state = USB_STATE_IDLE;

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_INIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_init(void) {

    // Enable USB
    usb_enable();

    // Reset interrupts
    usb_reset_interrupts();

    // Set configuration
    usb_set_configuration(0);

    // Enable interrupts
    usb_enable_interrupts();
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_ENABLE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_enable(void) {

    // Enable USB controller
    SLEEP |= SLEEP_USB_EN;

    // Enable USB
    P1DIR |= 1;
    P1_0 = 1;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_ABORT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_abort(void) {

    // Reset byte counts
    usb_n_bytes_in = 0;
    usb_n_bytes_out = 0;

    // Update USB state
    usb_state = USB_STATE_IDLE;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_STALL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_stall(void) {

    // Send stall packet
    USBCS0 |= USBCS0_SEND_STALL;

    // Update status
    usb_state = USB_STATE_STALL;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_RESET_INTERRUPTS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_reset_interrupts(void) {

    // Reset any pending interrupts
    USBIIF = 0;
    USBOIF = 0;
    USBCIF = 0;
    USBIF = 0;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_ENABLE_INTERRUPTS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_enable_interrupts(void) {

    // Enable control and IN EP interrupts
    USBIIE = USB_EP0IE | USB_INEP1IE | USB_INEP5IE;

    // Enable OUT EP interrupts
    USBOIE = USB_OUTEP4IE;

    // Enable reset interrupts
    USBCIE = USBCIE_RSTIE;

    // Enable interrupts
    IEN2 |= IEN2_USBIE;
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
    usb_set_ep(USB_EP_INT);
    USBMAXI = USB_SIZE_EP_INT / 8;
    USBMAXO = USB_SIZE_EP_INT / 8;

    // Set maximum packet sizes and enable double buffering
    usb_set_ep(USB_EP_OUT);
    USBMAXI = 0;
    USBMAXO = USB_SIZE_EP_OUT / 8;
    //USBCSOH |= USBCSOH_OUT_DBL_BUF;

    // Set maximum packet sizes and enable double buffering
    usb_set_ep(USB_EP_IN);
    USBMAXI = USB_SIZE_EP_IN / 8;
    USBMAXO = 0;
    //USBCSIH |= USBCSIH_IN_DBL_BUF;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_GET_CONFIGURATION
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_get_configuration(void) {

    // Queue configuration
    usb_queue_byte(usb_device.configuration);
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_SET_ADDRESS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Note: address given by bits [0, 6].
*/
void usb_set_address(uint8_t address) {

    // Set address
    USBADDR = address;

    // Wait until address is set
    while (USBADDR != address) {
        NOP();
    }
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
                usb_n_bytes_in = descriptor[2];
            }

            // Otherwise
            else {

                // Read descriptor length
                usb_n_bytes_in = descriptor[0];
            }

            // Link data to descriptor
            usb_data_in = descriptor;

            // Exit
            return;
        }

        // Update pointer
        descriptor += descriptor[0];
    }

    // No descriptor found
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

    // Setup packet is 8 bytes long
    usb_n_bytes_out = 8;

    // Fill setup packet (without EOD signaling)
    usb_receive_bytes(0);
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

                // Link data with queue
                usb_data_in = usb_data_queue;
                
                // Update USB state
                usb_state = USB_STATE_SEND;
                break;

            // OUT
            case (USB_DIRECTION_OUT):

                // Link data with buffer
                usb_data_out = usb_data_buffer;

                // Set number of packets to receive
                usb_n_bytes_out = usb_setup_packet.length;

                // Update USB state
                usb_state = USB_STATE_RECEIVE;
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
    if (usb_n_bytes_out != 0) {

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
                            usb_queue_byte(0); // Device bus powered
                            usb_queue_byte(0); // Remote wake up disabled
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
                            usb_queue_byte(0); // Reserved for future use?
                            usb_queue_byte(0); // Reserved for future use?
                            break;

                        //case USB_REQUEST_CLEAR_FEATURE:
                        //    break;

                        //case USB_REQUEST_SET_FEATURE:
                        //    break;

                        case USB_REQUEST_GET_INTERFACE:
                            usb_queue_byte(0); // No alternative interfaces
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
                            usb_queue_byte(0); // Not halted
                            usb_queue_byte(0); // Not stalled
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
    if (usb_state == USB_STATE_SEND) {

        // If number of bytes to send is larger than asked by host
        usb_n_bytes_in = min(usb_n_bytes_in, usb_setup_packet.length);

        // Send first bytes
        usb_send_bytes(1);
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_QUEUE_BYTE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Queue IN byte for later access with IN data pointer.
*/
void usb_queue_byte(uint8_t byte) {

    // Queue byte in buffer
    usb_data_queue[usb_n_bytes_in++] = byte;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_SET_BYTE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_set_byte(uint8_t byte) {

    // Set byte to active EP FIFO
    USBFIFO[USB_INDEX << 1] = byte;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_GET_BYTE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
uint8_t usb_get_byte(void) {

    // Read and return byte from active EP FIFO
    return USBFIFO[USB_INDEX << 1];
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_SEND_BYTES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_send_bytes(uint8_t end) {

    // Initialize number of bytes to send and looping variable
    uint8_t n = 0;
    uint8_t i = 0;

    // Make sure last packet was picked up
    while (*usb_cc_in & usb_if_in) {
        NOP();
    }

    // Byte count must not exceed max
    n = min(usb_n_bytes_in, usb_size);

    // Loop on bytes
    for (i = 0; i < n; i++) {

        // Set byte
        usb_set_byte(*usb_data_in++);
    }

    // Byte set
    *usb_cc_in |= usb_if_in;

    // If last packet read
    if (usb_n_bytes_in < usb_size) {

        // If EOD signaling necessary
        if (end) {

            // End of data
            *usb_cc_in |= usb_if_eod;
        }

        // Update USB state
        usb_state = USB_STATE_IDLE;
    }

    // Diminish count of bytes remaining to send
    usb_n_bytes_in -= n;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_RECEIVE_BYTES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_receive_bytes(uint8_t end) {

    // Initialize number of bytes to receive and looping variable
    uint8_t n = 0;
    uint8_t i = 0;

    // Make sure packet is ready to be picked up
    while (!(*usb_cc_out & usb_if_out)) {
        NOP();
    }

    // Byte count must not exceed max
    n = min(usb_n_bytes_out, usb_size);

    // Loop on bytes
    for (i = 0; i < n; i++) {

        // Get byte
        *usb_data_out++ = usb_get_byte();
    }

    // Byte read
    *usb_cc_out &= ~usb_if_out;

    // If last packet read
    if (usb_n_bytes_out < usb_size && usb_n_bytes_out - n == 0) {

        // If EOD signaling necessary
        if (end) {

            // End of data
            *usb_cc_out |= usb_if_eod;
        }

        // Update USB state
        usb_state = USB_STATE_IDLE;
    }

    // Diminish count of bytes remaining to receive
    usb_n_bytes_out -= n;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_CONTROL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_control(void) {

    // Set control EP
    usb_set_ep(USB_EP_CONTROL);

    // Control transfer ends due to a premature end of control transfer or
    // EP receives an unexpected token during the data stage
    if (USBCS0 & USBCS0_SETUP_END) {

        // Reset flag
        USBCS0 |= USBCS0_CLR_SETUP_END;

        // Abort transfer
        usb_abort();
    }

    // EP is stalled
    if (USBCS0 & USBCS0_SENT_STALL) {

        // Reset flag
        USBCS0 &= ~USBCS0_SENT_STALL;

        // Abort transfer
        usb_abort();
    }

    // Data asked for
    if (usb_state == USB_STATE_SEND) {

        // Send data
        usb_send_bytes(1);
    }

    // Data ready
    if (USBCS0 & USBCS0_OUTPKT_RDY) {

        // Look at state
        switch (usb_state) {

            // If idle
            case (USB_STATE_IDLE):

                // Setup stage
                usb_setup();
                break;

            // If receive
            case (USB_STATE_RECEIVE):

                // Receive data
                usb_receive_bytes(1);
                break;
        }
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_INT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_int(void) {

    // Select EP
    usb_set_ep(USB_EP_INT);
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

        // Abort transfer
        usb_abort();
    }

    // Data ready
    if (usb_state == USB_STATE_SEND) {

        // Send packet
        usb_send_bytes(0);
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

        // Abort transfer
        usb_abort();
    }

    // Data ready
    if (USBCSOL & USBCSOL_OUTPKT_RDY) {

        // If idle
        if (usb_state == USB_STATE_IDLE) {

            // Link data to buffer
            usb_data_out = usb_data_buffer;

            // Update USB state
            usb_state = USB_STATE_RECEIVE;
        }

        // Read number of bytes waiting in FIFO
        usb_n_bytes_out = USBCNTL | ((USBCNTH & 7) << 8);

        // Update number of bytes to receive
        usb_n_bytes_in += usb_n_bytes_out;

        // Get packet
        usb_receive_bytes(0);

        // End of transfer
        if (usb_state == USB_STATE_IDLE) {

            // Reply with same data
            usb_data_in = usb_data_buffer;

            // Update USB state
            usb_state = USB_STATE_SEND;

            // Send packet
            usb_in();
        }
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_SET_EP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Note: EP range given by [0, 5].
*/
void usb_set_ep(uint8_t ep) {

    // If new EP required
    if (ep != USBINDEX) {

        // Set EP
        USBINDEX = ep;

        // Assign EP specific bytes and pointers
        switch (ep) {

            // Control
            case USB_EP_CONTROL:

                // Define max packet size
                usb_size = USB_SIZE_EP_CONTROL;

                // Link pointers to control/configure register
                usb_cc_in = &USBCS0;
                usb_cc_out = &USBCS0;

                // Define interrupt flags
                usb_if_in = USBCS0_INPKT_RDY;
                usb_if_out = USBCS0_OUTPKT_RDY;
                usb_if_eod = USBCS0_DATA_END;
                break;

            // INT
            case USB_EP_INT:

                // Define max packet size
                usb_size = USB_SIZE_EP_INT;

                // Link pointers to control/configure register
                usb_cc_in = &USBCSIL;
                usb_cc_out = &USBCSOL;

                // Define interrupt flags
                usb_if_in = USBCSIL_INPKT_RDY;
                usb_if_out = USBCSOL_OUTPKT_RDY;
                usb_if_eod = 0;
                break;

            // IN
            case USB_EP_IN:

                // Define max packet size
                usb_size = USB_SIZE_EP_IN;

                // Link pointers to control/configure register
                usb_cc_in = &USBCSIL;
                usb_cc_out = 0;

                // Define interrupt flags
                usb_if_in = USBCSIL_INPKT_RDY;
                usb_if_out = 0;
                usb_if_eod = 0;
                break;

            // OUT
            case USB_EP_OUT:

                // Define max packet size
                usb_size = USB_SIZE_EP_OUT;

                // Link pointers to control/configure register
                usb_cc_in = 0;
                usb_cc_out = &USBCSOL;

                // Define interrupt flags
                usb_if_in = 0;
                usb_if_out = USBCSOL_OUTPKT_RDY;
                usb_if_eod = 0;
                break;
        }
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_ISR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Warning: interrupts shared with port 2!
*/
void usb_isr(void) __interrupt P2INT_VECTOR {

    // Check for reset flag
    if (USBCIF & USBCIF_RSTIF) {

        // Enable interrupts ?
        usb_enable_interrupts();
    }

    // Check for control EP0 flags
    if (USBIIF & USB_EP0IF) {

        // Control sequence
        usb_control();
    }

    // Check for INT EP1 flags
    if (USBIIF & USB_INEP1IF) {

        // Interrupt sequence (notification?)
        usb_int();
    }

    // Check for OUT EP4 flags
    if (USBOIF & USB_OUTEP4IF) {

        // Data to device sequence
        usb_out();
    }

    // Check for IN EP5 flags
    if (USBIIF & USB_INEP5IF) {

        // Data to host sequence
        usb_in();
    }

    // Reset interrupts
    usb_reset_interrupts();
}