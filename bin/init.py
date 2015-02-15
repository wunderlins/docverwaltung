#!/usr/bin/env python

import os.path
import sqlite3
import logging
import ConfigParser
from passlib.hash import pbkdf2_sha256

scandocconfpath = "../etc/scandoc.conf"
authenticationconfigpath = "../etc/authentication.conf"
authorisationconfigpath = "../etc/authorisation.conf"



# acl.db und licence.db erstellen und initialisieren.

# scandoc.conf einlesen
scandocconfig = ConfigParser.ConfigParser()
scandocconfig.read(scandocconfpath)
logfile = scandocconfig.get("default", "initlogfile")
licensedb = scandocconfig.get("default", "licensedb")
datagroupdb = os.path.normpath(scandocconfig.get("default", "datagroupdb"))
adminuser = scandocconfig.get("init", "adminuser")
adminpw = scandocconfig.get("init", "adminpw")
workdir = os.path.normpath(scandocconfig.get("init", "workdir"))
datadir = os.path.normpath(scandocconfig.get("init", "datadir"))
del scandocconfig

# authentication.conf einlesen
authenticationconfig = ConfigParser.ConfigParser()
authenticationconfig.read(authenticationconfigpath)
authenticationdb = os.path.normpath(authenticationconfig.get("default", "authenticationdb"))
hashingrounds = int(authenticationconfig.get("hashing", "rounds"))
hashingsalt = int(authenticationconfig.get("hashing", "salt_size"))
del authenticationconfig

# authorisation.conf einlesen
authorisationconfig = ConfigParser.ConfigParser()
authorisationconfig.read(authorisationconfigpath)
authorisationdb = os.path.normpath(authorisationconfig.get("default", "authorisationdb"))
del authorisationconfig

# Logging
logging.basicConfig(filename=logfile,format='%(asctime)s %(levelname)s:%(message)s' ,level=logging.DEBUG)

# Admin Passwort hashen
adminpwhash = pbkdf2_sha256.encrypt(adminpw, rounds=hashingrounds, salt_size=hashingsalt)

# Wenn Files schon existieren diese zu .old umbenennen und neues File erstellen.
try:
	if os.path.isfile(licensedb):
		os.rename(licensedb, licensedb + ".old")
		logging.warning(licensedb + " existiete bereits und wurde zu" + licensedb + ".old" + " umbenannt")

# Ueberpruefen ob authenticationdb authorisationdb und datagroupdb im selben file sind und diese umbenennen.
	dbfiles = sorted(set([datagroupdb, authenticationdb, authorisationdb]))
	for x in dbfiles:
		if os.path.isfile(x):
			os.rename(x, x + ".old")
			logging.warning(x + " existiete bereits und wurde zu " + x + ".old" + " umbenannt")
except:
	logging.exception('Umbenennen der Files funktioniert nicht')
	raise

# license.db erstellen
qry = open('./SQL/create_license.sql', 'r').read()
conn = sqlite3.connect(licensedb)
cur = conn.cursor()
cur.executescript(qry)
conn.commit()
cur.close()
conn.close()
logging.info(licensedb + " wurde erstellt")

# authentication DB erstellen
qry = open('./SQL/create_user.sql', 'r').read()
conn = sqlite3.connect(authenticationdb)
cur = conn.cursor()
cur.executescript(qry)
logging.info(authenticationdb + " user table wurde erstellt")
# adminbenutzer anlegen
cur.execute("INSERT INTO user (id, username, password, entry_created, entry_modified) VALUES (1, \'%s\', \'%s\', DATETIME(\'now\'), DATETIME(\'now\'));" %(adminuser, adminpwhash))
logging.info("Benutzer " + adminuser + " wurde erstellt")
conn.commit()
cur.close()
conn.close()

# authorisation DB erstellen
qry = open('./SQL/create_permission.sql', 'r').read()
conn = sqlite3.connect(authorisationdb)
cur = conn.cursor()
cur.executescript(qry)
logging.info(authorisationdb + " permission table wurde erstellt")
# berechtigung setzen
cur.execute("INSERT INTO permission (user_id, permissionname, input, output, entry_created, entry_modified) VALUES (1, \'administrator\', \'True\', \'True\', DATETIME(\'now\'), DATETIME(\'now\'));")
logging.info("gruppe administrator wurde erstellt")
conn.commit()
cur.close()
conn.close()

# datagroup DB erstellen
qry = open('./SQL/create_datagroup.sql', 'r').read()
conn = sqlite3.connect(datagroupdb)
cur = conn.cursor()
cur.executescript(qry)
logging.info(datagroupdb + " datagroup table wurde erstellt")
# datengruppe hinzufuegen
cur.execute("INSERT INTO datagroup (user_id, datagroupname, inputpath, outputpath, entry_created, entry_modified) VALUES (1, \'%s\', \'%s\', \'%s\', DATETIME(\'now\'), DATETIME(\'now\'));" %(adminuser, os.path.join(workdir, adminuser), os.path.join(datadir, adminuser)))

logging.info("Dem Benutzer %s wurde das workdir=%s und datadir=%s zugeteilt" %(adminuser, os.path.join(workdir, adminuser), os.path.join(datadir, adminuser)))
conn.commit()
cur.close()
conn.close()

# Ordner erstellen
if not os.path.exists(workdir):
	os.makedirs(workdir)
	logging.info("Ordner %s erstellt" %workdir)
if not os.path.exists(datadir):
	os.makedirs(datadir)
	logging.info("Ordner %s erstellt" %datadir)
if not os.path.exists(os.path.join(workdir, adminuser)):
	os.makedirs(os.path.join(workdir, adminuser))
	logging.info("Ordner %s erstellt" %(os.path.join(workdir, adminuser)))
if not os.path.exists(os.path.join(datadir, adminuser)):
	os.makedirs(os.path.join(datadir, adminuser))
	logging.info("Ordner %s erstellt" %(os.path.join(datadir, adminuser)))
logging.shutdown()

