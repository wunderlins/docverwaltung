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
