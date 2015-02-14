#!/usr/bin/env python

import sqlite3
import logging
from passlib.hash import pbkdf2_sha256


acldb = "../etc/acl.db"
logfile = "../var/auth.log"

# Logging
logging.basicConfig(filename=logfile,format='%(asctime)s %(levelname)s:%(message)s' ,level=logging.DEBUG)

# Authentisiert gegen acl.db
def internal(user, passwd):
	conn = sqlite3.connect(acldb)
	cur = conn.cursor()
	cur.execute("SELECT password FROM user WHERE username=\'%s\';" %user)
	try:
		pwhash = str(cur.fetchone()[0])
	except:
		logging.warning("Benutzer %s ist nicht bekannt" %user)
		cur.close()
		conn.close()
		return False
	if pbkdf2_sha256.verify(passwd, pwhash):
		logging.info("Benutzer %s wurde erfolgreich authentisiert" %user)
		cur.close()
		conn.close()
		return True
	else:
		logging.info("Benutzer %s konnte nicht authentisiert werden" %user)
		cur.close()
		conn.close()
		return False

# Authentisiert gegen ldap
def ldap(user, passwd):
	#TODO Hier muss noch etwas programmiert werden xD
	return False


