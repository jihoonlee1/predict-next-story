import json
import contextlib
import sqlite3


statements = [
"""
CREATE TABLE IF NOT EXISTS companies(
	id           INTEGER NOT NULL PRIMARY KEY,
	name         TEXT    NOT NULL,
	description  TEXT,
	industry     TEXT    NOT NULL,
	country      TEXT    NOT NULL,
	revenue      INTEGER NOT NULL,
	profits      INTEGER NOT NULL,
	assets       INTEGER NOT NULL,
	market_value INTEGER NOT NULL
);
""",
"""
CREATE TABLE IF NOT EXISTS company_alias(
	company_id INTEGER NOT NULL REFERENCES companies(id),
	alias      TEXT    NOT NULL,
	PRIMARY KEY(company_id, alias)
);
""",
"""
CREATE TABLE IF NOT EXISTS roots(
	id         INTEGER NOT NULL PRIMARY KEY,
	company_id INTEGER NOT NULL REFERENCES companies(id),
	content    TEXT    NOT NULL
);
""",
"""
CREATE TABLE IF NOT EXISTS root_children_positive0(
	id         INTEGER NOT NULL PRIMARY KEY,
	root_id    INTEGER NOT NULL REFERENCES root_events(id),
	company_id INTEGER NOT NULL REFERENCES companies(id),
	content    TEXT    NOT NULL
);
""",
"""
CREATE TABLE IF NOT EXISTS root_children_negative0(
	id         INTEGER NOT NULL PRIMARY KEY,
	root_id    INTEGER NOT NULL REFERENCES root_events(id),
	company_id INTEGER NOT NULL REFERENCES companies(id),
	content    TEXT    NOT NULL
);
""",
"""
CREATE TABLE IF NOT EXISTS root_children_negative1(
	id         INTEGER NOT NULL PRIMARY KEY,
	root_id    INTEGER NOT NULL REFERENCES root_events(id),
	company_id INTEGER NOT NULL REFERENCES companies(id),
	content    TEXT    NOT NULL
);
""",
"""
CREATE TABLE IF NOT EXISTS root_children_negative2(
	id         INTEGER NOT NULL PRIMARY KEY,
	root_id    INTEGER NOT NULL REFERENCES root_events(id),
	company_id INTEGER NOT NULL REFERENCES companies(id),
	content    TEXT    NOT NULL
);
""",
"""
CREATE TABLE IF NOT EXISTS root_children_negative3(
	id         INTEGER NOT NULL PRIMARY KEY,
	root_id    INTEGER NOT NULL REFERENCES root_events(id),
	company_id INTEGER NOT NULL REFERENCES companies(id),
	content    TEXT    NOT NULL
);
"""
]


def connect(database="database2.sqlite", mode="rw"):
	return contextlib.closing(sqlite3.connect(f"file:{database}?mode={mode}", uri=True))


def _add_companies(con, cur):
	with open("companies.json", "r") as f:
		companies = json.load(f)
		for c in companies:
			try:
				desc = c["description"].strip()
			except:
				desc = None
			name = c["organizationName"].strip()
			industry = c["industry"].strip()
			country = c["country"].strip()
			revenue = c["revenue"]
			profits = c["profits"]
			assets = c["assets"]
			market_value = c["marketValue"]
			cur.execute("SELECT ifnull(max(id)+1, 0) FROM companies")
			company_id, = cur.fetchone()
			cur.execute("INSERT INTO companies VALUES(?,?,?,?,?,?,?,?,?)",
				(company_id, name, desc, industry, country, revenue, profits, assets, market_value))
		con.commit()


def _add_alias(con, cur):
	with open("company_alias.json", "r") as f:
		companies = json.load(f)
		for company in companies:
			company_id = company["company_id"]
			alias = company["alias"]
			for item in alias:
				cur.execute("INSERT OR IGNORE INTO company_alias VALUES(?,?)", (company_id, item))
		con.commit()


def main():
	with connect(mode="rwc") as con:
		cur = con.cursor()
		for st in statements:
			cur.execute(st)
		_add_companies(con, cur)
		_add_alias(con, cur)


if __name__ == "__main__":
	main()
