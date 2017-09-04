#! /usr/bin/python
# -*- coding: utf-8 -*-

import usb.core

# Find stick
stick = usb.core.find(idVendor = 0x0451, idProduct = 0x16A7)

# No stick found
if stick is None:

	# Raise error
	raise ValueError("No stick found.")

# Otherwise
else:

	# Show stick
	print stick