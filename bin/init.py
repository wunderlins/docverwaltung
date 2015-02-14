#!/usr/bin/env python

import os.path
import sqlite3
import logging


# acl.db und licence.db erstellen und initialisieren.

licensedb = "../etc/license.db"
acldb = "../etc/acl.db"
logfile = "../var/init.log"

adminuser = "admin"
adminpw = "$pbkdf2-sha256$2000$tRaC0LpXKgVg7N27F6LUOg$ClwBPf.D2OiEfySh2f9DJtgFqhL2YDhVhD2O9sbCjbw" # PW = 'admin'
workdir = "../workdir"
datadir = "../datadir"

# Logging
logging.basicConfig(filename=logfile,format='%(asctime)s %(levelname)s:%(message)s' ,level=logging.DEBUG)

# Wenn Files schon existieren diese zu .old umbenennen und neues File erstellen.
try:
	if os.path.isfile(licensedb):
		os.rename(licensedb, licensedb + ".old")
		logging.warning(licensedb + " existiete bereits und wurde zu" + licensedb + ".old" + " umbenannt")
	if os.path.isfile(acldb):
		os.rename(acldb, acldb + ".old")
		logging.warning(acldb + " existiete bereits und wurde zu " + acldb + ".old" + " umbenannt")
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

# acl.db erstellen
qry = open('./SQL/create_acl.sql', 'r').read()
conn = sqlite3.connect(acldb)
cur = conn.cursor()
cur.executescript(qry)
logging.info(acldb + " wurde erstellt")
# adminbenutzer anlegen
cur.execute("INSERT INTO user (id, username, password, entry_created, entry_modified) VALUES (1, \'%s\', \'%s\', DATETIME(\'now\'), DATETIME(\'now\'));" %(adminuser, adminpw))
logging.info("Benutzer " + adminuser + " wurde erstellt")
# berechtigung setzen
cur.execute("INSERT INTO permission (user_id, permissionname, entry_created, entry_modified) VALUES (1, \'administrator\', DATETIME(\'now\'), DATETIME(\'now\'));")
logging.info("gruppe administrator wurde erstellt")
# datengruppe hinzufuegen
cur.execute("INSERT INTO datagroup (user_id, datagroupname, inputpath, outputpath, input, output, entry_created, entry_modified) VALUES (1, \'%s\', \'%s\', \'%s\', \'True\', \'True\', DATETIME(\'now\'), DATETIME(\'now\'));" %(adminuser, workdir + "/" + adminuser, datadir + "/" + adminuser))
logging.info("Dem Benutzer " + adminuser + " wurde das workdir=" + workdir + "/" + adminuser + " und datadir=" + datadir + "/" + adminuser + " zugeteilt")
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
if not os.path.exists(workdir + "/" + adminuser):
	os.makedirs(workdir + "/" + adminuser)
	logging.info("Ordner %s erstellt" %workdir + "/" + adminuser)
if not os.path.exists(datadir + "/" + adminuser):
	os.makedirs(datadir + "/" + adminuser)
	logging.info("Ordner %s erstellt" %datadir + "/" + adminuser)

