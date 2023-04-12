import contextlib
import sqlite3


dbname = "database.sqlite"
statements = [
"""
CREATE TABLE companies(
	id           INTEGER NOT NULL PRIMARY KEY,
	name         TEXT    NOT NULL,
	description  TEXT,
	industry     TEXT,
	country      TEXT,
	revenue      INTEGER,
	profits      INTEGER,
	assets       INTEGER,
	market_value INTEGER
);
""",
"""
CREATE TABLE incidents(
	id         INTEGER NOT NULL PRIMARY KEY,
	content    TEXT    NOT NULL,
	company_id INTEGER NOT NULL
)
""",
"""
CREATE TABLE root_incidents(
	id         INTEGER NOT NULL PRIMARY KEY,
	company_id INTEGER NOT NULL REFERENCES companies(id)
)
""",
"""
CREATE TABLE incidents_relevant(
	root_incident_id  INTEGER NOT NULL,
	child_incident_id INTEGER NOT NULL,
	incident_order    INTEGER NOT NULL,
	company_id        INTEGER NOT NULL,
	PRIMARY KEY(root_incident_id, child_incident_id)
)
""",
"""
CREATE TABLE incidents_irrelevant(
	root_incident_id  INTEGER NOT NULL,
	child_incident_id INTEGER NOT NULL,
	company_id        INTEGER NOT NULL,
	PRIMARY KEY(root_incident_id, child_incident_id)
)
"""
]


def connect(database=dbname, mode="rw"):
	return contextlib.closing(sqlite3.connect(f"file:{database}?mode={mode}", uri=True))


def main():
	with connect(mode="rwc") as con:
		cur = con.cursor()
		for st in statements:
			cur.execute(st)


if __name__ == "__main__":
	main()
