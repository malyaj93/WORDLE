-- $ sqlite3 words.db < words.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS Words;
CREATE TABLE IF NOT EXISTS Words (
    id INTEGER PRIMARY KEY,
    word CHAR(5)
);

-- loop through json here to add words to db
INSERT INTO Words(id, word) VALUES()