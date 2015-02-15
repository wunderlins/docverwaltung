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
