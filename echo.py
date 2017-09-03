#! /usr/bin/python
# -*- coding: utf-8 -*-

import usb.core

# Find stick
stick = usb.core.find(idVendor = 0x1d50, idProduct = 0x8001)

# No stick found
if stick is None:

	# Raise error
	raise ValueError("No stick found.")

# Otherwise
else:

	# Show stick
	print stick