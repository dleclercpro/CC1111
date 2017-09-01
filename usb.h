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

// USB setup masks
#define USB_SETUP_DIRECTION (1 << 7)
#define USB_SETUP_TYPE      (3 << 5)
#define USB_SETUP_RECIPIENT (31 << 0)

// USB types
#define USB_TYPE_STANDARD   (0 << 5)
#define USB_TYPE_CLASS      (1 << 5)
#define USB_TYPE_VENDOR     (2 << 5)
#define USB_TYPE_RESERVED   (3 << 5)

// USB recipients
#define USB_RECIPIENT_DEVICE    0
#define USB_RECIPIENT_INTERFACE 1
#define USB_RECIPIENT_EP        2
#define USB_RECIPIENT_OTHER     3

// USB standard device requests
#define USB_REQUEST_DEVICE_GET_STATUS        0
#define USB_REQUEST_DEVICE_CLEAR_FEATURE     1
#define USB_REQUEST_DEVICE_SET_FEATURE       3
#define USB_REQUEST_DEVICE_SET_ADDRESS       5
#define USB_REQUEST_DEVICE_GET_DESCRIPTOR    6
#define USB_REQUEST_DEVICE_SET_DESCRIPTOR    7
#define USB_REQUEST_DEVICE_GET_CONFIGURATION 8
#define USB_REQUEST_DEVICE_SET_CONFIGURATION 9

// USB standard interface requests
#define USB_REQUEST_INTERFACE_GET_STATUS    0
#define USB_REQUEST_INTERFACE_CLEAR_FEATURE 1
#define USB_REQUEST_INTERFACE_SET_FEATURE   3
#define USB_REQUEST_INTERFACE_GET_INTERFACE 10
#define USB_REQUEST_INTERFACE_SET_INTERFACE 17

// USB standard EP requests
#define USB_REQUEST_EP_GET_STATUS    0
#define USB_REQUEST_EP_CLEAR_FEATURE 1
#define USB_REQUEST_EP_SET_FEATURE   3
#define USB_REQUEST_EP_SYNCH_FRAME   18

// USB descriptors
#define USB_DESC_DEVICE           1
#define USB_DESC_CONFIGURATION    2
#define USB_DESC_STRING           3
#define USB_DESC_INTERFACE        4
#define USB_DESC_ENDPOINT         5
#define USB_DESC_DEVICE_QUALIFIER 6
#define USB_DESC_OTHER_SPEED      7
#define USB_DESC_INTERFACE_POWER  8

#define USB_TRANSFER_CONTROL     0
#define USB_TRANSFER_ISOCHRONOUS 1
#define USB_TRANSFER_BULK        2
#define USB_TRANSFER_INTERRUPT   3

#define USB_SIZE_EP_CONTROL 32
#define USB_SIZE_EP_INT     8
#define USB_SIZE_EP_IN      64
#define USB_SIZE_EP_OUT     64

#define USB_ADDRESS_EP_CONTROL 0 // Not used
#define USB_ADDRESS_EP_INT     1
#define USB_ADDRESS_EP_OUT     5
#define USB_ADDRESS_EP_IN      5

#define USB_DIRECTION_IN  (1 << 7)
#define USB_DIRECTION_OUT (0 << 0)

#define USB_MAX_POWER 50 // Maximum power in mA

void usb_init(void);
void usb_enumerate(void);
void usb_ep_in(void);
void usb_end_transaction(void);
void usb_select_ep(uint8_t address);
void usb_setup(void);
void usb_control(void);
void usb_int(void);
void usb_in(void);
void usb_out(void);
void usb_isr(void) __interrupt P2INT_VECTOR;

#endif