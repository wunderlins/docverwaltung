-- Createscript fuer ACL
-- Table user
CREATE TABLE IF NOT EXISTS user
(
id INTEGER PRIMARY KEY,
username TEXT,
password TEXT,
entry_created DATETIME,
entry_modified DATETIME,
entry_deleted DATETIME
);
-- Table permission
CREATE TABLE IF NOT EXISTS permission
(
id INTEGER PRIMARY KEY,
user_id INTEGER,
permissionname TEXT,
input BOOLEAN DEFAULT False,
output BOOLEAN DEFAULT False,
entry_created DATETIME,
entry_modified DATETIME,
entry_deleted DATETIME
);
-- Table datagroup
CREATE TABLE IF NOT EXISTS datagroup
(
id INTEGER PRIMARY KEY,
user_id INTEGER,
datagroupname TEXT,
inputpath TEXT,
outputpath TEXT,
entry_created DATETIME,
entry_modified DATETIME,
entry_deleted DATETIME
);

