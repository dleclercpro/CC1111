#! /usr/bin/python
# -*- coding: utf-8 -*-

import usb.core

# Find stick
stick = usb.core.find(idVendor = 0xBAE0, idProduct = 0xBAE0)

# No stick found
if stick is None:

	# Raise error
	raise ValueError("No stick found.")