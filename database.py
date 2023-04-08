import contextlib
import sqlite3


dbpath = "database.sqlite"
statements = [
"""
CREATE TABLE IF NOT EXISTS companies(
	id   INTEGER NOT NULL PRIMARY KEY,
	name TEXT    NOT NULL
);
""",
"""
CREATE TABLE IF NOT EXISTS incidents(
	id         INTEGER NOT NULL PRIMARY KEY,
	content    TEXT    NOT NULL,
	company_id INTEGER NOT NULL
)
""",
"""
CREATE TABLE IF NOT EXISTS events(
	id          INTEGER NOT NULL PRIMARY KEY,
	company_id  INTEGER NOT NULL,
	is_relevant INTEGER NOT NULL
);
""",
"""
CREATE TABLE IF NOT EXISTS event_incident(
	event_id    INTEGER NOT NULL,
	incident_id INTEGER NOT NULL,
	story_order INTEGER NOT NULL,
	PRIMARY KEY(event_id, incident_id)
);
"""
]


def connect(database=dbpath, mode="rw"):
	con = sqlite3.connect(f"file:{database}?mode={mode}", uri=True)
	cur = con.cursor()
	cur.execute("BEGIN TRANSACTION")
	cur.execute("PRAGMA foreign_keys = 1")
	cur.execute("COMMIT TRANSACTION")
	return contextlib.closing(con)


def main():
	with connect(mode="rwc") as con:
		cur = con.cursor()
		for st in statements:
			cur.execute(st)


if __name__ == "__main__":
	main()
