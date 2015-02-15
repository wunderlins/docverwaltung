#!/usr/bin/env python

import authentication

user = "admin"
password = "admin"

# Wenn Anmeldung nicht funktionierte gib False zurueck, ansonsten den Benutzernamen
def login():
	k = authentication.auth()
	if k.auth(user, password):
		return [user, k.UserID]
	else:
		return False
