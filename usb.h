#ifndef _USB_H_
#define _USB_H_

#include "cc1111.h"
#include "lib.h"

// USB bit masks
#define USB_INEP5IE (1 << 5)
#define USB_INEP4IE (1 << 4)
#define USB_INEP3IE (1 << 3)
#define USB_INEP2IE (1 << 2)
#define USB_INEP1IE (1 << 1)
#define USB_EP0IE   (1 << 0)

#define USB_OUTEP5IE (1 << 5)
#define USB_OUTEP4IE (1 << 4)
#define USB_OUTEP3IE (1 << 3)
#define USB_OUTEP2IE (1 << 2)
#define USB_OUTEP1IE (1 << 1)

#define USB_INEP5IF (1 << 5)
#define USB_INEP4IF (1 << 4)
#define USB_INEP3IF (1 << 3)
#define USB_INEP2IF (1 << 2)
#define USB_INEP1IF (1 << 1)
#define USB_EP0IF   (1 << 0)

#define USB_OUTEP5IF (1 << 5)
#define USB_OUTEP4IF (1 << 4)
#define USB_OUTEP3IF (1 << 3)
#define USB_OUTEP2IF (1 << 2)
#define USB_OUTEP1IF (1 << 1)

// USB descriptors
#define USB_DESC_DEVICE			  1
#define USB_DESC_CONFIGURATION	  2
#define USB_DESC_STRING			  3
#define USB_DESC_INTERFACE		  4
#define USB_DESC_ENDPOINT		  5
#define USB_DESC_DEVICE_QUALIFIER 6
#define USB_DESC_OTHER_SPEED      7
#define USB_DESC_INTERFACE_POWER  8

#define USB_TRANSFER_CONTROL     0
#define USB_TRANSFER_ISOCHRONOUS 1
#define USB_TRANSFER_BULK        2
#define USB_TRANSFER_INTERRUPT   3

#define USB_SIZE_EP_CONTROL 32
#define USB_SIZE_EP_INT	    8
#define USB_SIZE_EP_IN      64
#define USB_SIZE_EP_OUT     64

#define USB_ADDRESS_EP_CONTROL 0 // Not used
#define USB_ADDRESS_EP_INT 	   1
#define USB_ADDRESS_EP_OUT     5
#define USB_ADDRESS_EP_IN      5

#define USB_IN  (1 << 7)
#define USB_OUT (0 << 0)

#define USB_MAX_POWER 50 // Maximum power in mA

void usb_init(void);
void usb_enumerate(void);
void usb_ep_in(void);
void usb_end_transaction(void);
void usb_isr(void) __interrupt P2INT_VECTOR;

#endif