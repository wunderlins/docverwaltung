#!/usr/bin/env python

import os
import sqlite3
import subprocess
import datetime
import ConfigParser
import logging
import login
import authorisation
from PyPDF2 import PdfFileReader, PdfFileMerger

scannerconfpath = "../etc/scanner.conf"
scandocconfpath = "../etc/scandoc.conf"


# Klasse zum scanen, editieren und zu PDF umwandeln (inkl. OCR)
class scandoc(object):
	# Statische Member
	# Statische Methode
	# Dies ist der Konstruktor
	def __init__(self):
		# scandoc.conf einlesen
		scandocconfig = ConfigParser.ConfigParser()
		scandocconfig.read(scandocconfpath)
		logfile = scandocconfig.get("default", "scandoclogfile")
		self.__datagroupdb = scandocconfig.get("default", "datagroupdb")
		del scandocconfig
		# Logging
		logging.basicConfig(filename=logfile,format='%(asctime)s %(name)s %(levelname)s:%(message)s' ,level=logging.DEBUG)
		self.__scandoclog=logging.getLogger("scandoc")
		self.__scandoclog.info("#################  Log beginnt  #################")
		# Login
		result = login.login()
		if not result:
			self.__scandoclog.error("Login funktionierte nicht. Programm wird beendet.")
			exit(1)
		self.__user = result[0]
		self.__userid = result[1]
		self.__scandoclog.info("Benutzer %s wurde angemeldet" %self.__user)
		# Darf er scannen?
		self.__authorisation = authorisation.authorisation()
		if not self.__authorisation.authorisation("scan", self.__userid):
			exit(1)
		# Workdir setzen
		conn = sqlite3.connect(self.__datagroupdb)
		cur = conn.cursor()
		self.__scanfolder = str(cur.execute("SELECT inputpath FROM datagroup WHERE user_id=%s" %self.__userid).fetchone()[0])
		self.__scandoclog.info("scanfolder = %s" %self.__scanfolder)
		self.__dbfile = os.path.join(self.__scanfolder, "index.db")
		self.__scandoclog.info("index.db path = %s" %self.__dbfile)
		cur.close()
		conn.close()
		# DB oeffnen oder erstellen
		self.__conn = sqlite3.connect(self.__dbfile)
		self.__cur = self.__conn.cursor()
		try:
			self.__cur.execute("SELECT * FROM intsequence where name='lastfile';")
			self.__scandoclog.info("%s existierte bereits" %self.__dbfile)
		except:
			qry = open('./SQL/create_scandb.sql', 'r').read()
			self.__cur.executescript(qry)
			self.__conn.commit()
			self.__scandoclog.info("%s wurde neu erstellt" %self.__dbfile)
		self.__Test = "Hello World"
		# scanner.conf einlesen
		self.__scannerconfig = ConfigParser.ConfigParser()
		try:
			self.__scannerconfig.read(scannerconfpath)
			self.__scan_device = self.__scannerconfig.get("default", "scan_device")
			self.__scandoclog.info("scanner.conf eingelesen. Verwendeter scanner: %s" %self.__scan_device)
		except:
			self.__scandoclog.exception("scanner.conf konnte nicht gelesen werden")
			exit(1)
			
		

	# Dies ist der Destruktor
	def __del__(self):
		self.__cur.close()
		self.__conn.close()
		del self.__authorisation
		self.__scandoclog.info("#################  Log endet  #################")
		logging.shutdown()
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
		# ueberpruefen ob an deisem Tag schon gescannt wurde
		x = self.__cur.execute("select value from datesequence where name=\'lastdate\';")
		lastdate = datetime.datetime.strptime(x.fetchone()[0], "%Y-%m-%d %H:%M:%S")
		scan_batch = datetime.datetime.strftime(lastdate, "%Y%m%d")
		self.__scandoclog.info("Letzter Scanbatch startete %s" %scan_batch)
		# Wenn noch nichts gescannt wurde
		if not lastdate.date() == datetime.datetime.now().date():
			lastdate = datetime.datetime.now()
			scan_batch = lastdate.strftime("%Y%m%d-")
			self.__scandoclog.info("Heute wurde noch nichts gescannt %s" %scan_batch)
			scan_batchstart = "1000"
			self.__cur.execute("UPDATE datesequence SET value=\'%s\' WHERE name=\'lastdate\';" % lastdate.strftime("%Y-%m-%d %H:%M:%S"))
			self.__cur.execute("UPDATE intsequence SET value=%s WHERE name=\'lastfile\';" % scan_batchstart)
			self.__conn.commit()
		lastfile = self.__cur.execute("select value from intsequence where name=\'lastfile\';")
		scan_batchstart = str(int(lastfile.fetchone()[0]) + 1)
		self.__scandoclog.info("Batch beginnt mit der Nummer: %s" %scan_batchstart)
		batchfilename = os.path.join(self.__scanfolder, (scan_batch + "%d." + self.__scannerconfig.get("default", "scan_format")))
		try:		
			output = subprocess.Popen(["scanimage", "-b", "-d", self.__scan_device, "--source", self.__scannerconfig.get("default", "scan_source"), "--page-width", self.__scannerconfig.get("default", "scan_width"), "--page-height", self.__scannerconfig.get("default", "scan_height"), "-x", self.__scannerconfig.get("default", "scan_x"), "-y", self.__scannerconfig.get("default", "scan_y"), "--batch=" + batchfilename, "--format=" + self.__scannerconfig.get("default", "scan_format"), "--mode", self.__scannerconfig.get("default", "scan_mode"), "--resolution", self.__scannerconfig.get("default", "scan_resolution"), "--batch-start=" + scan_batchstart, "--swdespeck", self.__scannerconfig.get("default", "scan_swdespeck"), "--swskip", self.__scannerconfig.get("default", "scan_swskip"), "--swdeskew=" + self.__scannerconfig.get("default", "scan_swdeskew"), "--ald=" + self.__scannerconfig.get("default", "scan_ald")], stderr=subprocess.PIPE)
		except:
			self.__scandoclog.exception("beim scannen ging etwas schief...")
			exit(1)
	
		# sequence in DB erhoehen
		seiten = output.stderr.read().splitlines
		for x in seiten(0):
			self.__scandoclog.info(x)
			if x[:7] == "Scanned":
				self.__cur.execute("INSERT INTO scans (filename) VALUES (\'%s%s.%s\')" %(scan_batch, x[13:17], self.__scannerconfig.get("default", "scan_format")))
				self.__cur.execute("UPDATE intsequence SET value=%s WHERE name=\'lastfile\';" % x[13:17])
				self.__conn.commit()
		self.__scandoclog.info("Scanjob beendet")
	# Scans bearbeiten und Thumbnail erstellen
	def prepare(self):
		toprepare = self.__cur.execute("SELECT filename FROM scans WHERE prepared=\'False\';")
		for x in toprepare.fetchall():
			p = subprocess.Popen(["mogrify", "-normalize", "-level", "27%,76%", self.__scanfolder + x[0]])
			self.__cur.execute("UPDATE scans SET prepared=\'True\' WHERE filename=\'%s\';" %x[0])
			self.__conn.commit()
			p.communicate()

	# Thunpnails erstellen
	def thumbnail(self):
		toprepare = self.__cur.execute("SELECT filename FROM scans WHERE thumbnail=\'False\';")
		for x in toprepare.fetchall():
			p = subprocess.Popen(["convert", "-thumbnail", self.__thumbnailsize, self.__scanfolder + x[0], self.__scanfolder + x[0][:14] + self.__thumbnailformat])
			self.__cur.execute("UPDATE scans SET thumbnail=\'True\' WHERE filename=\'%s\';" %x[0])
			self.__conn.commit()
			p.communicate()

	# OCR
	def ocr(self):
		toocr = self.__cur.execute("SELECT filename FROM scans WHERE ocr=\'False\';")
		for x in toocr.fetchall():
			p = subprocess.Popen(["tesseract", "-l", "deu", "-psm", "3", self.__scanfolder + x[0], self.__scanfolder + x[0][:13], "pdf"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
	def merge(self, outpath, pdf_files):
		merger = PdfFileMerger()
		for filename in pdf_files:
   			merger.append(PdfFileReader(os.path.join(outpath, filename), "rb"))
		merger.write(os.path.join(outpath, "merged_full.pdf"))













