#!/usr/bin/env python

import sqlite3
import logging
import ConfigParser
import os.path
from passlib.hash import pbkdf2_sha256



class auth(object):
	# Statische Member
	# Statische Methode
	# Dies ist der Konstruktor
	def __init__(self):
		# Logging
		self.__authlog = logging.getLogger("authentication")
		# authentication.conf einlesen
		confpath = os.path.join(os.path.dirname(__file__), '..','etc','authentication.conf')
		self.__config = ConfigParser.ConfigParser()
		try:
			self.__config.read(confpath)
			self.__auth_type = self.__config.get("default", "authentication_type")
			self.__authlog.info("authentication.conf eingelesen. Verwendete Authentication: %s" %self.__auth_type)
		except:
			self.__authlog.exception("authentication.conf konnte nicht gelesen werden")
			exit(1)
		self.__user = ""
		self.__passwd = ""
		self.__userid = ""
	# Dies ist der Destruktor
	def __del__(self):
		del self.__config
	# Hier sind die Methoden
	# Getter Methoden
	def userid(self):
		return self.__userid
	# Setter Methoden
	def auth(self, user, passwd):
		self.__user = user
		self.__passwd = passwd
		if self.__auth_type == "internal":
			return self.__internal()
		else:
			self.__authlog.error("Authentication %s ist nicht implementiert" %self.__auth_type)
			exit(1)
	# Property Attribute
	UserID = property(userid)
	# Alle weiteren Methoden
	### Funktionen #############################################
	# Authentisiert gegen acl.db
	def __internal(self):
		conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), (self.__config.get("default", "authenticationdb"))))
		cur = conn.cursor()
		cur.execute("SELECT password FROM user WHERE username=\'%s\';" %self.__user)
		try:
			pwhash = str(cur.fetchone()[0])
		except:
			self.__authlog.warning("Benutzer %s ist nicht bekannt" %self.__user)
			cur.close()
			conn.close()
			return False
		if pbkdf2_sha256.verify(self.__passwd, pwhash):
			self.__authlog.info("Benutzer %s wurde erfolgreich authentisiert" %self.__user)
			cur.execute("SELECT id FROM user WHERE username=\'%s\';" %self.__user)
			self.__userid = int(cur.fetchone()[0])
			cur.close()
			conn.close()
			return True
		else:
			self.__authlog.info("Benutzer %s konnte nicht authentisiert werden" %self.__user)
			cur.close()
			conn.close()
			return False

	# Authentisiert gegen ldap
	def __ldap(self):
		#TODO Hier muss noch etwas programmiert werden xD
		return False


