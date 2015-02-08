#!/usr/bin/env python

import sqlite3
import subprocess
import datetime


# Pfade
scanfolder = "/home/samuel/Documents/scan/scan/test/"
dbfile = scanfolder + "index.db"

# Createscript fuer DB
createscriptscan = ["""\
CREATE TABLE IF NOT EXISTS scans
(
id INTEGER PRIMARY KEY,
filename TEXT,
time_created TEXT,
prepared BOOLEAN DEFAULT False,
ocr BOOLEAN DEFAULT False
);""", """\
CREATE TABLE IF NOT EXISTS sequence
(
id INTEGER PRIMARY KEY,
name TEXT,
value INTEGER
);""", """\
INSERT INTO sequence (name, value) VALUES ('lastfile', 1000); 
"""]

createscriptpdf = ["""\
CREATE TABLE IF NOT EXISTS folder
(
id INTEGER PRIMARY KEY,
name TEXT
);""", """\
INSERT INTO folder (name) VALUES ('bank1'); 
""", """\
INSERT INTO folder (name) VALUES ('bank2'); 
""", """\
INSERT INTO folder (name) VALUES ('bank3'); 
""", """\
INSERT INTO folder (name) VALUES ('creditcard1'); 
""", """\
INSERT INTO folder (name) VALUES ('creditcard2'); 
""", """\
INSERT INTO folder (name) VALUES ('car'); 
""", """\
INSERT INTO folder (name) VALUES ('job'); 
""", """\
INSERT INTO folder (name) VALUES ('insurance1'); 
""", """\
INSERT INTO folder (name) VALUES ('insurance2'); 
"""]

# Klasse zum scanen, editieren und zu PDF umwandeln (inkl. OCR)
class scandoc(object):
	# Statische Member
	# Statische Methode
	# Dies ist der Konstruktor
	def __init__(self):
		# DB oeffnen oder erstellen
		self.__conn = sqlite3.connect(dbfile)
		self.__cur = self.__conn.cursor()
		try:
			self.__cur.execute("SELECT * FROM sequence where name='lastfile';")
		except:
			for x in createscriptscan:
				self.__cur.execute(x)
			self.__conn.commit()	
		self.__Test = "Hello World"
		# Einstellungen fuer Scanner (Fujitsu ScanSnap S1500)
		self.__scan_device = "fujitsu"				# Selects the device.
		self.__scan_source = "ADF Duplex"			# Selects the scan source (such as a document-feeder).
													# ADF Front|ADF Back|ADF Duplex
		self.__scan_format = "tiff"					# File format of output file
													# pnm|tiff
		self.__scan_mode = "color"					# Selects the scan mode (e.g., lineart, monochrome, or color).
													# Lineart|Halftone|Gray|Color
		self.__scan_resolution = "150"				# Sets the resolution of the scanned image.
													# 50..600dpi (in steps of 1)
		self.__scan_width = "210.009"				# Specifies the width of the media.  Required for automatic centering of sheet-fed scans.
													# 0..221.121mm (in steps of 0.0211639)
		self.__scan_height = "297.014"				# Specifies the height of the media.
													# 0..876.695mm (in steps of 0.0211639)
		self.__scan_x = self.__scan_width			# Width of scan-area.
													# 0..215.872mm (in steps of 0.0211639)
		self.__scan_y = self.__scan_height			# Height of scan-area.
													# 0..279.364mm (in steps of 0.0211639)
		self.__scan_batch = "out%d"					# Filename
		self.__scan_batchstart = "1000"				# page number to start naming files with
		self.__scan_swdespeck = "1"					# Maximum diameter of lone dots to remove from scan.
													# 0..9 (in steps of 1)
		self.__scan_swskip = "15%"					# Request driver to discard pages with low percentage of dark pixels
													# 0..100% (in steps of 1.52588e-05)
		self.__scan_swdeskew = "no"					# Request driver to rotate skewed pages digitally.
		self.__scan_ald = "yes" 					# Scanner detects paper lower edge. May confuse some frontends.



	# Dies ist der Destruktor
	def __del__(self):
		self.__conn.close()
	# Hier sind die Methoden
	# Getter Methoden
	def test(self):
		return self.__Test
	# Setter Methoden
	def setTest(self, test):
		self.__Test = test
	# Property Attribute
	Test = property(test, setTest)
	# Alle weiteren Methoden
	### Funktionen #############################################
	### Scan ###
	def scan(self):
		scan_batch = datetime.datetime.now().strftime("%Y%m%d-")
		lastfile = self.__cur.execute("select value from sequence where name=\'lastfile\';")
		scan_batchstart = str(int(lastfile.fetchone()[0]) + 1)
		output = subprocess.Popen(["scanimage", "-b", "-d", self.__scan_device, "--source", self.__scan_source, "--page-width", self.__scan_width, "--page-height", self.__scan_height, "-x", self.__scan_x, "-y", self.__scan_y, "--batch=" + self.__scanfolder + self.__scan_batch + "%d." + self.__scan_format, "--format=" + self.__scan_format, "--mode", self.__scan_mode, "--resolution", self.__scan_resolution, "--batch-start=" + self.__scan_batchstart, "--swdespeck", self.__scan_swdespeck, "--swskip", self.__scan_swskip, "--swdeskew=" + self.__scan_swdeskew, "--ald=" + self.__scan_ald], stderr=subprocess.PIPE)

	
		# sequence in DB erhoehen
		seiten = output.stderr.read().splitlines
		for x in seiten(0):
			if x[:7] == "Scanned":
				self.__cur.execute("INSERT INTO scans (filename) VALUES (\'%s%s.%s\')" %(self.__scan_batch, x[13:17], self.__scan_format))
				self.__cur.execute("UPDATE sequence SET value=%s WHERE name=\'lastfile\';" % x[13:17])
				self.__conn.commit()
	# Scans bearbeiten
	def prepare(self):
		toprepare = self.__cur.execute("SELECT filename FROM scans WHERE prepared=\'False\';")
		for x in toprepare.fetchall():
			p = subprocess.Popen(["mogrify", "-normalize", "-level", "27%,76%", scanfolder + x[0]])
			self.__cur.execute("UPDATE scans SET prepared=\'True\' WHERE filename=\'%s\';" %x[0])
			self.__conn.commit()
			p.communicate()
	# OCR
	def ocr(self):
		toocr = self.__cur.execute("SELECT filename FROM scans WHERE ocr=\'False\';")
		for x in toocr.fetchall():
			p = subprocess.Popen(["tesseract", "-l", "deu", "-psm", "3", scanfolder + x[0], scanfolder + x[0][:13], "pdf"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			self.__cur.execute("UPDATE scans SET ocr=\'True\' WHERE filename=\'%s\';" %x[0])
			self.__conn.commit()
			p.communicate()



# Klasse zum zusammenfuehren und verschieben von PDFs
class pdfmanipulation(object):
	# Statische Member
	# Statische Methode
	# Dies ist der Konstruktor
	def __init__(self):
		# DB oeffnen oder erstellen
		self.__conn = sqlite3.connect("manipulation.db")
		self.__cur = self.__conn.cursor()
		try:
			self.__cur.execute("SELECT * FROM folder';")
		except:
			for x in createscriptpdf:
				self.__cur.execute(x)
			self.__conn.commit()	
		self.__Test = "Hello World"
	# Dies ist der Destruktor
	def __del__(self):
		self.__conn.close()
	# Hier sind die Methoden
	# Getter Methoden
	def test(self):
		return self.__Test
	# Setter Methoden
	def setTest(self, test):
		self.__Test = test
	# Property Attribute
	Test = property(test, setTest)
	# Alle weiteren Methoden
	### Funktionen #############################################
	### Scan ###
	def hello(self):
		return "hello world"













