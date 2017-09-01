#include "usb.h"

// USB setup
struct usb_setup {
    uint8_t info;
    uint8_t request;
    uint16_t value;
    uint16_t index;
    uint16_t size;
};

// Generate instance of USB setup
__xdata static struct usb_setup usb_setup;

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
    le_word(67),            // Length in bytes of data returned
    2,                      // Number of interfaces
    1,                      // Configuration argument
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
    7,                                     // Size
    USB_DESC_ENDPOINT,                     // Type
    USB_DIRECTION_IN | USB_ADDRESS_EP_INT, // Direction and address
    USB_TRANSFER_INTERRUPT,                // Transfer type
    le_word(USB_SIZE_EP_INT),              // Max packet size
    255,                                   // Polling interval in frames

    // Data EP OUT
    7,                                      // Size
    USB_DESC_ENDPOINT,                      // Type
    USB_DIRECTION_OUT | USB_ADDRESS_EP_OUT, // Direction and address
    USB_TRANSFER_BULK,                      // Transfer type
    le_word(USB_SIZE_EP_OUT),               // Max packet size
    0,                                      // Polling interval in frames (none)

    // Data EP IN
    7,                                    // Size
    USB_DESC_ENDPOINT,                    // Type
    USB_DIRECTION_IN | USB_ADDRESS_EP_IN, // Direction and address
    USB_TRANSFER_BULK,                    // Transfer type
    le_word(USB_SIZE_EP_IN),              // Max packet size
    0,                                    // Polling interval in frames (none)

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

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_INIT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Note: USB IN/OUT EP interrupts enabled by default
*/
void usb_init(void) {

    // Enable USB controller
    SLEEP |= SLEEP_USB_EN;

    // Enable control and IN EP interrupts
    USBIIE = USB_EP0IE | USB_INEP1IE | USB_INEP5IE;

    // Enable OUT EP interrupts
    USBOIE = USB_OUTEP5IE;

    // Enable reset interrupts
    USBCIE = USBCIE_RSTIE;

    // Enable interrupts
    IEN2 |= IEN2_USBIE;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_ENUMERATE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_enumerate(void) {

}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_EP_IN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Note: EP range given by [0, 5]
*/
void usb_ep_in(uint8_t ep) {

    // Set EP
    USBINDEX = ep & 0x0F;

    // Set max packet size
    USBMAXI = USB_IN_SIZE;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_EP_OUT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Note: EP range given by [0, 5]
*/
void usb_ep_in(uint8_t ep) {

    // Set EP
    USBINDEX = ep & 0x0F;

    // Set max packet size
    USBMAXO = USB_OUT_SIZE;
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
    USB_SELECT_EP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_select_ep(uint8_t address) {

    // Select EP
    USBINDEX = address;
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_GET_DESCRIPTOR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_get_descriptor(uint16_t x) {

    // Get type and index
    uint8_t type = x >> 8; // MSB
    uint8_t index = x & 255; // LSB

    // Initialize looping index
    uint8_t i = 0;

    // Loop on descriptors
    while (usb_descriptors[i] != 0) {

        // Compare types
        if (usb_descriptors[i + 1] == type && usb_descriptors[i + 2] == index) {

        }

        // Update index
        i += usb_descriptors[i];
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_SETUP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_setup(void) {

    // Type
    switch (usb_setup.info & USB_SETUP_TYPE) {

        // Standard
        case USB_TYPE_STANDARD:

            // Recipient
            switch (usb_setup.info & USB_SETUP_RECIPIENT) {

                // Device
                case USB_RECIPIENT_DEVICE:

                    // Request
                    switch (usb_setup.request) {

                        case USB_REQUEST_DEVICE_GET_STATUS:
                            break;

                        case USB_REQUEST_DEVICE_CLEAR_FEATURE:
                            break;

                        case USB_REQUEST_DEVICE_SET_FEATURE:
                            break;

                        case USB_REQUEST_DEVICE_SET_ADDRESS:
                            break;

                        case USB_REQUEST_DEVICE_GET_DESCRIPTOR:
                            break;

                        case USB_REQUEST_DEVICE_SET_DESCRIPTOR:
                            break;

                        case USB_REQUEST_DEVICE_GET_CONFIGURATION:
                            break;

                        case USB_REQUEST_DEVICE_SET_CONFIGURATION:
                            break;
                    }

                    break;

                // Interface
                case USB_RECIPIENT_INTERFACE:

                    // Request
                    switch (usb_setup.request) {

                        case USB_REQUEST_INTERFACE_GET_STATUS:
                            break;

                        case USB_REQUEST_INTERFACE_CLEAR_FEATURE:
                            break;

                        case USB_REQUEST_INTERFACE_SET_FEATURE:
                            break;

                        case USB_REQUEST_INTERFACE_GET_INTERFACE:
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

        // Class
        case USB_TYPE_CLASS:

            switch (usb_setup.request) {

                case 0:
                    break;

                case 1:
                    break;
            }

            break;
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_CONTROL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_control(void) {

    // Select control EP
    usb_select_ep(USB_ADDRESS_EP_CONTROL);

    // A control transfer ends due to a premature end of control transfer or
    // EP0 receives an unexpected token during the Data stage
    if (USBCS0 & USBCS0_SETUP_END) {

        // Clear setup end bit
        USBCS0 |= USBCS0_CLR_SETUP_END;
    }

    // Error: a STALL has been sent
    if (USBCS0 & USBCS0_SENT_STALL) {

        // Clear flag
        USBCS0 &= ~USBCS0_SENT_STALL;
    }

    // A data packet that was loaded into the EP0 FIFO has been sent to the
    // USB host
    if (USBCS0 & USBCS0_INPKT_RDY) {

    }

    // Data packet has been received
    if (USBCS0 & USBCS0_OUTPKT_RDY) {

        // Unload Setup packet from EP0 FIFO

        // Examine contents and perform operations

        // End of setup stage
        USBSC0 |= USBCS0_CLR_OUTPKT_RDY;

        // Control transfer has no Data stage
        USBSC0 |= USBSC0_DATA_END;
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_INT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_int(void) {
    NOP();
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_IN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_in(void) {
    NOP();
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    USB_OUT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_out(void) {
    NOP();
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

    // EP5
    if (USBIIF & USB_INEP5IF) {

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