-- Createscript fuer license
-- Table license
CREATE TABLE IF NOT EXISTS license
(
id INTEGER PRIMARY KEY,
module TEXT,
quantity INTEGER,
active BOOLEAN DEFAULT False,
entry_created DATETIME,
entry_modified DATETIME,
entry_deleted DATETIME
);
-- Initialisierung
-- maximale Benutzerzahl
INSERT INTO license (module, quantity, active, entry_created, entry_modified) VALUES ('maxuser', 1, 'True', DATETIME('now'), DATETIME('now'));

