#!/usr/bin/env python

import pyinsane.abstract as pyinsane

devices = pyinsane.get_devices()
assert(len(devices) > 0)
device = devices[1]
scanner_id = device.name
device.options['resolution'].value = 300
scan_session = device.scan(multiple=False)

