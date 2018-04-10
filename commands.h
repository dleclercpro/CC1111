#ifndef _COMMANDS_H_
#define _COMMANDS_H_

#include "led.h"
#include "usb.h"
#include "radio.h"

uint8_t command_get(void);
void command_do(uint8_t cmd);
void command_register_read(void);
void command_register_write(void);
void command_radio_receive(void);
void command_radio_send(void);
void command_radio_send_receive(void);
void command_led(void);
void command_test(void);

#endif