#!/usr/bin/env python

import os
import ConfigParser
import datetime
import subprocess

scannerconfpath = os.path.join(os.path.dirname(__file__), '..', 'etc', 'scanner.conf')
scandocconfpath = os.path.join(os.path.dirname(__file__), '..', 'etc', 'scandoc.conf')

def scan():
	scandocconfig = ConfigParser.ConfigParser()
	scandocconfig.read(scandocconfpath)
	scannerconfig = ConfigParser.ConfigParser()
	scannerconfig.read(scannerconfpath)
	
	datadir = scandocconfig.get('init','datadir')
	scan_batchstart = "1"
	batchname = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
	batchfilename = os.path.join(datadir, (batchname + "-%d." + scannerconfig.get("default", "scan_format")))
	params = [
						"scanimage", "-b",
						"-d", scannerconfig.get("default", "scan_device"), 
						"--source", scannerconfig.get("default", "scan_source"),
						"--page-width", scannerconfig.get("default", "scan_width"),
						"--page-height", scannerconfig.get("default", "scan_height"),
						"-x", scannerconfig.get("default", "scan_x"),
						"-y", scannerconfig.get("default", "scan_y"),
						"--batch=" + batchfilename,
						"--format=" + scannerconfig.get("default", "scan_format"),
						"--mode", scannerconfig.get("default", "scan_mode"),
						"--resolution", scannerconfig.get("default", "scan_resolution"),
						"--batch-start=" + scan_batchstart,
						"--swdespeck", scannerconfig.get("default", "scan_swdespeck"),
						"--swskip", scannerconfig.get("default", "scan_swskip"),
						"--swdeskew=" + scannerconfig.get("default", "scan_swdeskew"),
						"--ald=" + scannerconfig.get("default", "scan_ald")
						]
	
	
	
	
	try:
		output = subprocess.Popen(params, stderr=subprocess.PIPE)
	except:
		print "Da ging wohl was schief..."
		raise
	
