#!/usr/bin/env python

import sqlite3
import logging
import ConfigParser


class authorisation(object):
	# Statische Member
	# Statische Methode
	# Dies ist der Konstruktor
	def __init__(self):
		# Logging
		self.__authorisationlog = logging.getLogger("authorisation")
		# authorisation.conf einlesen
		confpath = "../etc/authorisation.conf"
		self.__config = ConfigParser.ConfigParser()
		try:
			self.__config.read(confpath)
			self.__authorisation_type = self.__config.get("default", "authorisation_type")
			self.__authorisationlog.info("authorisation.conf eingelesen. Verwendete authorisation: %s" %self.__authorisation_type)
		except:
			self.__authorisationlog.exception("authorisation.conf konnte nicht gelesen werden")
			exit(1)
	# Dies ist der Destruktor
	def __del__(self):
		del self.__config
	# Hier sind die Methoden
	# Getter Methoden
	def test(self):
		return self.__Test
	# Setter Methoden
	def setTest(self, test):
		self.__Test = test
	def authorisation(self, authtype, userid):
		self.__authtype = authtype
		self.__userid = userid
		if self.__authorisation_type == "internal":
			return self.__internal()
		else:
			self.__authorisationlog.error("authorisation %s ist nicht implementiert" %self.__authorisation_type)
			exit(1)
	# Property Attribute
	Test = property(test, setTest)
	# Alle weiteren Methoden
	### Funktionen #############################################
	# authorisationentisiert gegen acl.db
	def __internal(self):
		conn = sqlite3.connect(self.__config.get("default", "authorisationdb"))
		cur = conn.cursor()
		if not bool(cur.execute("SELECT input FROM permission WHERE user_id=%s" %str(self.__userid)).fetchone()[0]):
			self.__authorisationlog.error("BenutzerID %s ist nicht berechtigt zum scannen" %self.__userid)
			return False
		else:
			self.__authorisationlog.info("BenutzerID %s ist berechtigt zum scannen" %self.__userid)
			return True

	# authorisationentisiert gegen ldap
	def __ldap(self):
		#TODO Hier muss noch etwas programmiert werden xD
		return False


