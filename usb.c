#include "usb.h"

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
	USBIIE = USB_EP0IE | USB_INEP1IE;

	// Enable OUT EP interrupts
	USBOIE = USB_OUTEP1IE;

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
    USB_END_TRANSACTION
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
void usb_end_transaction(void) {

	// Send STALL
	USBCS0 |= USBCS0_SEND_STALL;
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

	}

	// Check for EP0 flag
	if (USBIIF & USB_EP0IF) {

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

	// Check for IN EP flags
	// EP1
	if (USBIIF & USB_INEP1IF) {

	}

	// Check for OUT EP flags
	// EP1
	if (USBOIF & USB_OUTEP1IF) {

	}

	// Clear corresponding CPU flags
	P2IFG = 0;
	USBIF = 0;
}

// USB descriptors
__xdata uint8_t usb_descriptors[] = {

	// Device descriptor
	18, 			     // Size
	USB_DESC_DEVICE,     // Type
	le_word(0x0200),     // USB specification number
	2,				     // Class
	0, 				     // Subclass
	0,				     // Protocol
	USB_SIZE_EP_CONTROL, // Max packet size for EP0
	le_word(0xBAE0),     // Vendor
	le_word(0xBAE0),     // Product
	le_word(0x0100),     // Release number
	1,				     // Manufacturer string descriptor index
	2,				     // Product string descriptor index
	3,				     // Serial number string descriptor index
	1,				     // Number of configurations

	// Configuration descriptor
	9,						// Size
	USB_DESC_CONFIGURATION, // Type
	le_word(67),			// Length in bytes of data returned
	2,						// Number of interfaces
	1,						// Configuration argument
	0,						// Configuration string descriptor (none)
	192,					// Power parameters for this configuration
	USB_MAX_POWER >> 1,		// Max power in 2mA units (divided by 2)

	// Interface descriptor 1 (control)
	9,					// Size
	USB_DESC_INTERFACE, // Type
	0,					// Interface number (start with zero, then increment)
	0,					// Alternative setting
	1,					// Number of EP for this interface
	2,					// Class
	2,					// Subclass
	1,					// Protocol
	0,					// Interface string descriptor (none)

	// Interface descriptor 2 (data)
	9,					// Size
	USB_DESC_INTERFACE, // Type
	1,					// Interface number
	0,					// Alternative setting
	2,					// Number of EP for this interface
	10,					// Class (data)
	0,					// Subclass
	0,					// Protocol
	0,					// Interface string descriptor (none)

	// Notification EP
	7,						     // Size
	USB_DESC_ENDPOINT,		     // Type
	USB_IN | USB_ADDRESS_EP_INT, // Direction and address
	USB_TRANSFER_INTERRUPT,	     // Transfer type
	le_word(USB_SIZE_EP_INT),    // Max packet size
	255,					     // Polling interval in frames (interrupt only)

	// Data EP OUT
	7,						      // Size
	USB_DESC_ENDPOINT,		      // Type
	USB_OUT | USB_ADDRESS_EP_OUT, // Direction and address
	USB_TRANSFER_BULK,		      // Transfer type
	le_word(USB_SIZE_EP_OUT),	  // Max packet size
	0,					          // Polling interval in frames (ignore)

	// Data EP IN
	7,						    // Size
	USB_DESC_ENDPOINT,		    // Type
	USB_IN | USB_ADDRESS_EP_IN, // Direction and address
	USB_TRANSFER_BULK,		    // Transfer type
	le_word(USB_SIZE_EP_IN),	// Max packet size
	0,					        // Polling interval in frames (ignore)

	// String descriptors
	4,				 // Size
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
};