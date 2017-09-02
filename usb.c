#include "usb.h"

// USB descriptors
__xdata static const uint8_t usb_descriptors[153] = {

    // Device descriptor
    18,                  // Size
    USB_DESC_DEVICE,     // Type
    le_word(0x0200),     // USB specification number
    2,                   // Class
    0,                   // Subclass
    0,                   // Protocol
    USB_SIZE_EP_CONTROL, // Max packet size for EP0
    le_word(0xBAE0),     // Vendor
    le_word(0xBAE0),     // Product
    le_word(0x0100),     // Release number
    1,                   // Manufacturer string descriptor index
    2,                   // Product string descriptor index
    3,                   // Serial number string descriptor index
    1,                   // Number of configurations

    // Configuration descriptor
    9,                      // Size
    USB_DESC_CONFIGURATION, // Type
    le_word(48),            // Total length (configuration, interfaces and EPs)
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
    le_word(USB_SIZE_EP_INT),      // Max packet size
    255,                           // Polling interval in frames

    // Data EP OUT
    7,                              // Size
    USB_DESC_ENDPOINT,              // Type
    USB_DIRECTION_OUT | USB_EP_OUT, // Direction and address
    USB_TRANSFER_BULK,              // Transfer type
    le_word(USB_SIZE_EP_OUT),       // Max packet size
    0,                              // Polling interval in frames (none)

    // Data EP IN
    7,                            // Size
    USB_DESC_ENDPOINT,            // Type
    USB_DIRECTION_IN | USB_EP_IN, // Direction and address
    USB_TRANSFER_BULK,            // Transfer type
    le_word(USB_SIZE_EP_IN),      // Max packet size
    0,                            // Polling interval in frames (none)

    // String descriptors
    4,               // Size
    USB_DESC_STRING, // Type
    le_word(0x1009), // Language (EN-CA)

    // String descriptor (manufacturer)
    60,
    USB_DESC_STRING,
    le_word("k"),
    le_word("e"),
    le_word("i"),
    le_word("n"),
    le_word("e"),
    le_word("c"),
    le_word("h"),
    le_word("t"),
    le_word("e"),
    le_word("r"),
    le_word("d"),
    le_word("e"),
    le_word("u"),
    le_word("t"),
    le_word("s"),
    le_word("c"),
    le_word("h"),
    le_word("e"),
    le_word("r"),
    le_word("@"),
    le_word("g"),
    le_word("m"),
    le_word("a"),
    le_word("i"),
    le_word("l"),
    le_word("."),
    le_word("c"),
    le_word("o"),
    le_word("m"),

    // String descriptor (product)
    14,
    USB_DESC_STRING,
    le_word("C"),
    le_word("C"),
    le_word("1"),
    le_word("1"),
    le_word("1"),
    le_word("1"),

    // String descriptor (serial)
    8,
    USB_DESC_STRING,
    le_word("0"),
    le_word("0"),
    le_word("1"),

    // EOD
    0
};

// USB device
struct usb_device {
    uint8_t configuration = 0;
    uint8_t interface = 0;
};

// USB setup
struct usb_setup {
    uint8_t type;
    uint8_t request;
    uint16_t value;
    uint16_t index;
    uint16_t length;
};

// Generate instance of USB device
__xdata static struct usb_setup usb_setup;

// Generate instance of USB setup
__xdata static struct usb_setup usb_setup;

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_INIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_init(void) {

    // Enable USB controller
    SLEEP |= SLEEP_USB_EN;

    // Reset any pending interrupts
    USBIIF = 0;
    USBOIF = 0;
    USBCIF = 0;

    // Enable control and IN EP interrupts
    USBIIE = USB_EP0IE | USB_INEP1IE | USB_INEP4IE;

    // Enable OUT EP interrupts
    USBOIE = USB_OUTEP5IE;

    // Enable reset interrupts
    USBCIE = USBCIE_RSTIE;

    // Enable interrupts
    IEN2 |= IEN2_USBIE;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_SET_CONFIGURATION
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_set_configuration(uint8_t value) {

    // Update device configuration (only one)
    usb_device.configuration = value;

    // Set max packet size for interrupt transfers
    usb_set_ep(USB_EP_INT, USB_SIZE_EP_INT, USB_SIZE_EP_INT);

    // Set max packet size for IN transfers
    usb_set_ep(USB_EP_IN, USB_SIZE_EP_IN, 0);

    // Set max packet size for OUT transfers
    usb_set_ep(USB_EP_OUT, 0, USB_SIZE_EP_OUT);
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
    USB_SET_EP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Note: EP range given by [0, 5].
*/
void usb_set_ep(uint8_t ep, uint8_t max_in, uint8_t max_out) {

    // Set EP
    USBINDEX = ep;

    // Only for EP [1, 5]
    if (ep != 0) {

        // Set maximum packet size for selected IN EP (in units of 8 bytes)
        USBMAXI = max_in / 8;

        // Set maximum packet size for selected OUT EP (in units of 8 bytes)
        USBMAXO = max_out / 8;
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_END_TRANSACTION
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_end_transaction(void) {

    // Send STALL
    USBCS0 |= USBCS0_SEND_STALL;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_GET_BYTE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
uint8_t usb_get_byte(void) {

    // Read and return byte from active EP FIFO
    switch (USBINDEX) {

        // EP0
        case USB_EP_CONTROL:
            return USBF0;

        // EP1
        case USB_EP_INT:
            return USBF1;

        // EP4
        case USB_EP_IN:
            return USBF4;

        // EP5
        case USB_EP_OUT:
            return USBF5;
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_GET_BYTES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
uint8_t usb_get_bytes(uint8_t n) {

    // Initialize looping variable
    uint8_t i;

    // Loop on bytes
    for (i = 0; i < n; i++) {

        // Get byte
        usb_get_byte();
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_SET_BYTE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_set_byte(uint8_t byte) {

    // Load chosen EP FIFO
    switch (USBINDEX) {

        // EP0
        case USB_EP_CONTROL:
            USBF0 = byte;

        // EP1
        case USB_EP_INT:
            USBF1 = byte;

        // EP4
        case USB_EP_IN:
            USBF4 = byte;

        // EP5
        case USB_EP_OUT:
            USBF5 = byte;
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_SET_BYTES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_set_bytes(uint8_t bytes, uint8_t n) {

    // Initialize looping variable
    uint8_t i;

    // Loop on bytes (from MSB to LSB)
    for (i = 1; i <= n; i++) {

        // Set byte
        usb_set_byte(bytes & (255 << (8 * (n - i))));
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_GET_SETUP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_get_setup_packet(void) {

    // Parse setup bytes and update setup structure
    usb_setup.type = usb_get_byte();
    usb_setup.request = usb_get_byte();
    usb_setup.value = (usb_get_byte() << 8) | usb_get_byte();
    usb_setup.index = (usb_get_byte() << 8) | usb_get_byte();
    usb_setup.length = (usb_get_byte() << 8) | usb_get_byte();
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

    // Initialize looping index
    uint8_t i = 0;

    // Loop on descriptors
    while (usb_descriptors[i] != 0) {

        // Compare types
        if (usb_descriptors[i + 1] == type && usb_descriptors[i + 2] == index) {

            // If asked for configuration descriptor
            if (type == USB_DESC_CONFIGURATION) {

                // Send descriptors
                usb_set_bytes(usb_descriptors[i], usb_descriptors[i + 2]);
            }

            // Otherwise
            else {

                // Send descriptor
                usb_set_bytes(usb_descriptors[i], usb_descriptors[i])
            }
        }

        // Update index
        i += usb_descriptors[i];
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_SETUP_TRANSACTION
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_setup_transaction(void) {

    // SETUP STAGE
    // Get setup packet
    usb_get_setup_packet();

    // Only respond to standard USB requests
    switch (usb_setup.type & USB_SETUP_TYPE) {

        // Standard
        case USB_TYPE_STANDARD:

            // Recipient
            switch (usb_setup.type & USB_SETUP_RECIPIENT) {

                // Device
                case USB_RECIPIENT_DEVICE:

                    // Request
                    switch (usb_setup.request) {

                        case USB_REQUEST_DEVICE_GET_STATUS:
                            usb_set_byte(0); // Device bus powered
                            usb_set_byte(0); // Remote wake up disabled
                            break;

                        case USB_REQUEST_DEVICE_CLEAR_FEATURE:
                            break;

                        case USB_REQUEST_DEVICE_SET_FEATURE:
                            break;

                        case USB_REQUEST_DEVICE_SET_ADDRESS:
                            usb_set_address(usb_setup.value);
                            break;

                        case USB_REQUEST_DEVICE_GET_DESCRIPTOR:
                            usb_get_descriptor(usb_setup.value);
                            break;

                        case USB_REQUEST_DEVICE_SET_DESCRIPTOR:
                            break;

                        case USB_REQUEST_DEVICE_GET_CONFIGURATION:
                            usb_set_byte(usb_device.configuration);
                            break;

                        case USB_REQUEST_DEVICE_SET_CONFIGURATION:
                            usb_set_configuration(usb_setup.value);
                            break;
                    }

                    break;

                // Interface
                case USB_RECIPIENT_INTERFACE:

                    // Request
                    switch (usb_setup.request) {

                        case USB_REQUEST_INTERFACE_GET_STATUS:
                            usb_set_byte(0); // Reserved for future use?
                            usb_set_byte(0); // Reserved for future use?
                            break;

                        case USB_REQUEST_INTERFACE_CLEAR_FEATURE:
                            break;

                        case USB_REQUEST_INTERFACE_SET_FEATURE:
                            break;

                        case USB_REQUEST_INTERFACE_GET_INTERFACE:
                            usb_set_byte(0); // No alternative interfaces
                            break;

                        case USB_REQUEST_INTERFACE_SET_INTERFACE:
                            break;
                    }

                    break;

                // Endpoint
                case USB_RECIPIENT_EP:

                    // Request
                    switch (usb_setup.request) {

                        case USB_REQUEST_EP_GET_STATUS:
                            usb_set_byte(0); // Not halted
                            usb_set_byte(0); // Not stalled
                            break;

                        case USB_REQUEST_EP_CLEAR_FEATURE:
                            break;

                        case USB_REQUEST_EP_SET_FEATURE:
                            break;

                        case USB_REQUEST_EP_SYNCH_FRAME:
                            break;
                    }

                    break;
            }

            break;
    }

    // DATA STAGE
    // If data
    if (usb_setup.length > 0) {

        // Read number of bytes received
        //uint8_t n = USBCNT0;

        // Done processing setup packet
        USBSC0 |= USBCS0_CLR_OUTPKT_RDY;

        // Packet ready to be picked up by host
        USBSC0 |= USBCS0_INPKT_RDY;
    }

    // Otherwise
    else {

        // Done processing setup packet and end of data
        USBSC0 |= USBCS0_CLR_OUTPKT_RDY | USBSC0_DATA_END;
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

    // Error: a STALL has been sent
    if (USBCS0 & USBCS0_SENT_STALL) {

        // Reset flag
        USBCS0 &= ~USBCS0_SENT_STALL;

        // Abort transfer
        NOP();
    }

    // A control transfer ends due to a premature end of control transfer or
    // EP0 receives an unexpected token during the data stage
    else if (USBCS0 & USBCS0_SETUP_END) {

        // Reset flag
        USBCS0 |= USBCS0_CLR_SETUP_END;

        // If new setup packet
        if (USBCS0 & USBCS0_OUTPKT_RDY) {

            // Setup stage
            usb_setup_transaction();
        }

        // Otherwise
        else {

            // Abort transfer
            NOP();
        }
    }

    // Otherwise normal setup
    else if (USBCS0 & USBCS0_OUTPKT_RDY) {

        // Setup stage
        usb_setup_transaction();
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_INT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_int(void) {

    // Select EP
    usb_ep_select(USB_EP_INT);

    // Set max packet size
    USBMAXI = USB_SIZE_EP_INT / 8;
    USBMAXO = 0;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_IN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_in(void) {

    // Select EP
    usb_ep_select(USB_EP_IN);

    // Set max packet size
    USBMAXI = USB_SIZE_EP_IN / 8;
    USBMAXO = 0;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_OUT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_out(void) {

    // Select EP
    usb_ep_select(USB_EP_OUT);

    // Set max packet size
    USBMAXI = 0;
    USBMAXO = USB_SIZE_EP_OUT / 8;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_ISR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Warning: interrupts shared with port 2!
*/
void usb_isr(void) __interrupt P2INT_VECTOR {

    // Check for common flags
    // Reset
    if (USBCIF & USBCIF_RSTIF) {
        NOP();
    }

    // Check for control flags
    // EP0
    if (USBIIF & USB_EP0IF) {

        // Control sequence
        usb_control();
    }

    // Check for IN EP flags
    // EP1
    if (USBIIF & USB_INEP1IF) {

        // Interrupt sequence (notification?)
        usb_int();
    }

    // EP4
    if (USBIIF & USB_INEP4IF) {

        // Data to host sequence
        usb_in();
    }

    // Check for OUT EP flags
    // EP5
    if (USBOIF & USB_OUTEP5IF) {

        // Data to device sequence
        usb_out();
    }

    // Clear corresponding CPU flags
    P2IFG = 0;
    USBIF = 0;
}