-- Createscript fuer scan index DB
CREATE TABLE IF NOT EXISTS scans
(
id INTEGER PRIMARY KEY,
filename TEXT,
time_created TEXT,
prepared BOOLEAN DEFAULT False,
thumbnail BOOLEAN DEFAULT False,
ocr BOOLEAN DEFAULT False
);
CREATE TABLE IF NOT EXISTS intsequence
(
id INTEGER PRIMARY KEY,
name TEXT,
value INTEGER
);
INSERT INTO intsequence (name, value) VALUES ('lastfile', 1000);
CREATE TABLE IF NOT EXISTS datesequence
(
id INTEGER PRIMARY KEY,
name TEXT,
value DATETIME
);
INSERT INTO datesequence (name, value) VALUES ('lastdate', DATETIME('now')); 

