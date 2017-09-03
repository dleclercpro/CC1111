#include "usb.h"

// USB descriptors
__xdata uint8_t usb_descriptors[] = {

    // Device descriptor
    18,                  // Size
    USB_DESC_DEVICE,     // Type
    LE_WORD(0x0200),     // USB specification number
    2,                   // Class
    0,                   // Subclass
    0,                   // Protocol
    USB_SIZE_EP_CONTROL, // Max packet size for EP0
    LE_WORD(USB_VID),    // Vendor
    LE_WORD(USB_PID),    // Product
    LE_WORD(0x0100),     // Release number
    1,                   // Manufacturer string descriptor index
    2,                   // Product string descriptor index
    3,                   // Serial number string descriptor index
    1,                   // Number of configurations

    // Configuration descriptor
    9,                      // Size
    USB_DESC_CONFIGURATION, // Type
    LE_WORD(48),            // Total length (configuration, interfaces and EPs)
    2,                      // Number of interfaces
    1,                      // Configuration index
    0,                      // Configuration string descriptor (none)
    192,                    // Power parameters for this configuration
    USB_MAX_POWER >> 1,     // Max power in 2mA units (divided by 2)

    // Interface descriptor 1 (control)
    9,                  // Size
    USB_DESC_INTERFACE, // Type
    0,                  // Interface number (start with zero, then increment)
    0,                  // Alternative setting
    1,                  // Number of EP for this interface
    2,                  // Class
    2,                  // Subclass
    1,                  // Protocol
    0,                  // Interface string descriptor (none)

    // Interface descriptor 2 (data)
    9,                  // Size
    USB_DESC_INTERFACE, // Type
    1,                  // Interface number
    0,                  // Alternative setting
    2,                  // Number of EP for this interface
    10,                 // Class (data)
    0,                  // Subclass
    0,                  // Protocol
    0,                  // Interface string descriptor (none)

    // Notification EP
    7,                             // Size
    USB_DESC_ENDPOINT,             // Type
    USB_DIRECTION_IN | USB_EP_INT, // Direction and address
    USB_TRANSFER_INTERRUPT,        // Transfer type
    LE_WORD(USB_SIZE_EP_INT),      // Max packet size
    10,                            // Polling interval in frames

    // Data EP OUT
    7,                              // Size
    USB_DESC_ENDPOINT,              // Type
    USB_DIRECTION_OUT | USB_EP_OUT, // Direction and address
    USB_TRANSFER_BULK,              // Transfer type
    LE_WORD(USB_SIZE_EP_OUT),       // Max packet size
    0,                              // Polling interval in frames (none)

    // Data EP IN
    7,                            // Size
    USB_DESC_ENDPOINT,            // Type
    USB_DIRECTION_IN | USB_EP_IN, // Direction and address
    USB_TRANSFER_BULK,            // Transfer type
    LE_WORD(USB_SIZE_EP_IN),      // Max packet size
    0,                            // Polling interval in frames (none)

    // String descriptors
    4,               // Size
    USB_DESC_STRING, // Type
    LE_WORD(0x1009), // Language (EN-CA)

    // String descriptor (manufacturer)
    60,
    USB_DESC_STRING,
    LE_WORD('k'),
    LE_WORD('e'),
    LE_WORD('i'),
    LE_WORD('n'),
    LE_WORD('e'),
    LE_WORD('c'),
    LE_WORD('h'),
    LE_WORD('t'),
    LE_WORD('e'),
    LE_WORD('r'),
    LE_WORD('d'),
    LE_WORD('e'),
    LE_WORD('u'),
    LE_WORD('t'),
    LE_WORD('s'),
    LE_WORD('c'),
    LE_WORD('h'),
    LE_WORD('e'),
    LE_WORD('r'),
    LE_WORD('@'),
    LE_WORD('g'),
    LE_WORD('m'),
    LE_WORD('a'),
    LE_WORD('i'),
    LE_WORD('l'),
    LE_WORD('.'),
    LE_WORD('c'),
    LE_WORD('o'),
    LE_WORD('m'),

    // String descriptor (product)
    14,
    USB_DESC_STRING,
    LE_WORD('C'),
    LE_WORD('C'),
    LE_WORD('1'),
    LE_WORD('1'),
    LE_WORD('1'),
    LE_WORD('1'),

    // String descriptor (serial)
    8,
    USB_DESC_STRING,
    LE_WORD('0'),
    LE_WORD('0'),
    LE_WORD('1'),

    // EOD
    0
};

// Generate instance of USB device
static struct usb_device usb_device;

// Generate instance of USB setup
static struct usb_setup_packet usb_setup_packet;

// Generate data pointers
static uint8_t *data_in;
static uint8_t *data_out;

// Generate data buffer (8 bytes)
static uint8_t data_buffer[8] = {0};

// Generate byte counts
static uint8_t n_bytes_in = 0;
static uint8_t n_bytes_out = 0;

// Generate state
static uint8_t usb_state = USB_STATE_IDLE;

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_INIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_init(void) {

    // Enable USB controller
    SLEEP |= SLEEP_USB_EN;

    // Enable USB
    P1DIR |= 1;
    P1_0 = 1;

    // Reset interrupts
    usb_reset_interrupts();

    // Set configuration
    usb_set_configuration(0);

    // Enable interrupts
    usb_enable_interrupts();
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_GET_BYTE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
uint8_t usb_get_byte(void) {

    // Initialize byte
    uint8_t byte = 0;

    // Read and return byte from active EP FIFO
    switch (USBINDEX) {

        // EP0
        case USB_EP_CONTROL:
            byte = USBF0;
            break;

        // EP1
        case USB_EP_INT:
            byte = USBF1;
            break;

        // EP4
        case USB_EP_IN:
            byte = USBF4;
            break;

        // EP5
        case USB_EP_OUT:
            byte = USBF5;
            break;
    }

    // Return it
    return byte;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_SET_BYTE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_set_byte(uint8_t byte) {

    // Set byte to active EP FIFO
    switch (USBINDEX) {

        // EP0
        case USB_EP_CONTROL:
            USBF0 = byte;
            break;

        // EP1
        case USB_EP_INT:
            USBF1 = byte;
            break;

        // EP4
        case USB_EP_IN:
            USBF4 = byte;
            break;

        // EP5
        case USB_EP_OUT:
            USBF5 = byte;
            break;
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
    data_buffer[n_bytes_in++] = byte;

    // Link data to buffer
    data_in = data_buffer;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_RECEIVE_BYTES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_receive_bytes(void) {

    // Read number of bytes remaining to receive
    uint8_t n = n_bytes_out;

    // Wait until bytes are ready to be read
    while ((USBCS0 & USBCS0_OUTPKT_RDY) == 0) {
        NOP();
    }

    // If byte count exceeds expectation
    if (n > USB_SIZE_EP_CONTROL) {

        // Update count
        n = USB_SIZE_EP_CONTROL;
    }

    // Diminish count of bytes remaining to send
    n_bytes_out -= n;

    // Loop on bytes
    while (n--) {

        // Get byte
        *data_out++ = usb_get_byte();
    }

    // Byte read
    USBCS0 |= USBCS0_CLR_OUTPKT_RDY;

    // If last byte read
    if (n_bytes_out == 0) {

        // End of data
        USBCS0 |= USBCS0_DATA_END;

        // Update USB state
        usb_state = USB_STATE_IDLE;
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_SEND_BYTES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_send_bytes(void) {

    // Initialize number of bytes remaining to send
    uint8_t n = n_bytes_in;

    // Wait until last bytes are picked up
    while (USBCS0 & USBCS0_INPKT_RDY) {
        NOP();
    }

    // If byte count exceeds max
    if (n_bytes_in > USB_SIZE_EP_CONTROL) {

        // Update count
        n = USB_SIZE_EP_CONTROL;
    }

    // Diminish count of bytes remaining to send
    n_bytes_in -= n;

    // Loop on bytes
    while (n--) {

        // Set byte
        usb_set_byte(*data_in++);
    }

    // Bytes ready
    USBCS0 |= USBCS0_INPKT_RDY;

    // If last byte sent
    if (n_bytes_in == 0) {

        // End of data
        USBCS0 |= USBCS0_DATA_END;

        // Update USB state
        usb_state = USB_STATE_IDLE;
    }
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

    // Set maximum packet sizes for selected EP
    usb_set_ep(USB_EP_INT);
    USBMAXI = USB_SIZE_EP_INT / 8;
    USBMAXO = USB_SIZE_EP_INT / 8;

    // Set maximum packet sizes for selected EP
    usb_set_ep(USB_EP_IN);
    USBMAXI = USB_SIZE_EP_IN / 8;
    USBMAXO = 0;

    // Set maximum packet sizes for selected EP
    usb_set_ep(USB_EP_OUT);
    USBMAXI = 0;
    USBMAXO = USB_SIZE_EP_OUT / 8;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_GET_CONFIGURATION
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_get_configuration(void) {

    // Queue configuration
    usb_queue_byte(usb_device.configuration);

    // Link data to buffer
    data_in = data_buffer;
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
                n_bytes_in = descriptor[2];
            }

            // Otherwise
            else {

                // Read descriptor length
                n_bytes_in = descriptor[0];
            }

            // Link data to descriptor
            data_in = descriptor;

            // Exit
            return;
        }

        // Update pointer
        descriptor += descriptor[0];
    }

    // No descriptor found
    NOP();
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_GET_SETUP_PACKET
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_get_setup_packet(void) {

    // Link data with USB setup
    data_out = (uint8_t *) &usb_setup_packet;

    // Setup packet is 8 bytes long
    n_bytes_out = 8; // USBCNT0 ?

    // Fill setup packet
    usb_receive_bytes();
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
                
                // Update USB state
                usb_state = USB_STATE_SEND;
                break;

            // OUT
            case (USB_DIRECTION_OUT):

                // Update USB state
                usb_state = USB_STATE_RECEIVE;
                break;
        }
    }

    // Otherwise
    else {

        // Update USB state
        usb_state = USB_STATE_IDLE;
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
        case USB_TYPE_CLASS:
            break;
    }

    // If data to send
    if (usb_state == USB_STATE_SEND) {

        // If number of bytes to send is larger than asked by host
        if (n_bytes_in > usb_setup_packet.length) {

            // Reassign it
            n_bytes_in = usb_setup_packet.length;
        }
    }

    // If data to receive
    else if (usb_state == USB_STATE_RECEIVE) {

        // Read number of bytes to receive
        n_bytes_out = usb_setup_packet.length;
    }
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
    // EP0 receives an unexpected token during the data stage
    if (USBCS0 & USBCS0_SETUP_END) {

        // Reset flag
        USBCS0 |= USBCS0_CLR_SETUP_END;

        // Update USB state
        usb_state = USB_STATE_IDLE;

        // Abort transfer
        return;
    }

    // EP0 is stalled
    if (USBCS0 & USBCS0_SENT_STALL) {

        // Reset flag
        USBCS0 &= ~USBCS0_SENT_STALL;

        // Update USB state
        usb_state = USB_STATE_IDLE;

        // Abort transfer
        return;
    }

    // Data asked for
    if (usb_state == USB_STATE_SEND) {

        // Send data
        usb_send_bytes();
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
                usb_receive_bytes();
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
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_OUT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_out(void) {

    // Select EP
    usb_set_ep(USB_EP_OUT);
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