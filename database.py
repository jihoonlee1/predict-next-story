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
CREATE TABLE IF NOT EXISTS central_articles(
	id             INTEGER  NOT NULL PRIMARY KEY,
	company_id     INTEGER  NOT NULL REFERENCES companies(id) ON DELETE CASCADE ON UPDATE CASCADE,
	title          TEXT     NOT NULL,
	body           TEXT     NOT NULL,
	unix_timestamp INTEGER  NOT NULL
);
""",
"""
CREATE TABLE IF NOT EXISTS chatgpt_generated_incidents(
	id         INTEGER NOT NULL PRIMARY KEY,
	company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE ON UPDATE CASCADE,
	content    TEXT    NOT NULL
);
""",
"""
CREATE TABLE IF NOT EXISTS events(
	id                 INTEGER NOT NULL PRIMARY KEY,
	central_article_id INTEGER NOT NULL REFERENCES central_articles(id) ON DELETE CASCADE ON UPDATE CASCADE,
	is_relevant        INTEGER NOT NULL
);
""",
"""
CREATE TABLE IF NOT EXISTS event_incident(
	event_id           INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE ON UPDATE CASCADE,
	incident_id        INTEGER NOT NULL REFERENCES chatgpt_generated_incidents(id) ON DELETE CASCADE ON UPDATE CASCADE,
	story_order        INTEGER NOT NULL,
	PRIMARY KEY(event_id, incident_id)
);
""",
"""
CREATE INDEX IF NOT EXISTS central_articles_index0 ON central_articles(company_id, id, title, body, unix_timestamp);
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
