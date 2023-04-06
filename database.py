import contextlib
import sqlite3


dbpath = "database.sqlite"
statements = [
"""
CREATE TABLE companies(
	id   INTEGER NOT NULL PRIMARY KEY,
	name TEXT    NOT NULL
);
""",
"""
CREATE TABLE central_articles(
	id             INTEGER  NOT NULL PRIMARY KEY,
	company_id     INTEGER  NOT NULL REFERENCES companies(id) ON DELETE CASCADE ON UPDATE CASCADE,
	title          TEXT     NOT NULL,
	body           TEXT     NOT NULL,
	unix_timestamp INTEGER  NOT NULL
);
""",
"""
CREATE TABLE chatgpt_generated_incidents(
	id                 INTEGER NOT NULL PRIMARY KEY,
	company_id         INTEGER NOT NULL REFERENCES companies(id)        ON DELETE CASCADE ON UPDATE CASCADE,
	central_article_id INTEGER NOT NULL REFERENCES central_articles(id) ON DELETE CASCADE ON UPDATE CASCADE,
	content            TEXT    NOT NULL
);
""",
"""
CREATE TABLE events(
	id             INTEGER NOT NULL,
	incident_id    INTEGER NOT NULL REFERENCES chatgpt_generated_incidents(id) ON DELETE CASCADE ON UPDATE CASCADE,
	is_relevant    INTEGER NOT NULL,
	incident_order INTEGER NOT NULL,
	PRIMARY KEY(id, incident_id)
);
""",
"""
CREATE TABLE where_am_i_company_id_sorted(
	idx INTEGER NOT NULL
);
""",
"""
CREATE INDEX central_articles_index0 ON central_articles(company_id, id, title, body, unix_timestamp);
"""
]


def connect(database=dbpath, mode="rw"):
	con = sqlite3.connect(f"file:{database}?mode={mode}", uri=True)
	cur = con.cursor()
	cur.execute("BEGIN TRANSACTION")
	cur.execute("PRAGMA foreign_keys = 1")
	cur.execute("COMMIT TRANSACTION")
	return contextlib.closing(con)


def initialize():
	with connect(mode="rwc") as con:
		cur = con.cursor()
		for st in statements:
			cur.execute(st)


def main():
	with connect(database="incidents.sqlite") as con0:
		cur0 = con0.cursor()
		cur0.execute()


if __name__ == "__main__":
	initialize()
