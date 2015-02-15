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
