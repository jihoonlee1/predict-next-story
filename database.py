import json
import contextlib
import pathlib
import sqlite3


dbpath = pathlib.Path("database.sqlite")
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
CREATE TABLE IF NOT EXISTS roots(
	id         INTEGER NOT NULL PRIMARY KEY,
	company_id INTEGER NOT NULL REFERENCES companies(id),
	content    TEXT    NOT NULL
);
""",
"""
CREATE TABLE IF NOT EXISTS children(
	id         INTEGER NOT NULL PRIMARY KEY,
	root_id    INTEGER NOT NULL REFERENCES roots(id),
	company_id INTEGER NOT NULL REFERENCES companies(id),
	content    TEXT    NOT NULL,
	pos_neg    INTEGER NOT NULL,
	from_gpt   INTEGER NOT NULL
)
"""
]


def connect(database=dbpath, mode="rw"):
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
			cur.execute("SELECT 1 FROM companies WHERE name = ?", (name, ))
			if cur.fetchone() is not None:
				break
			cur.execute("SELECT ifnull(max(id)+1, 0) FROM companies")
			company_id, = cur.fetchone()
			cur.execute("INSERT INTO companies VALUES(?,?,?,?,?,?,?,?,?)",
				(company_id, name, desc, industry, country, revenue, profits, assets, market_value))
		con.commit()


def initialize():
	if not dbpath.exists():
		with connect(mode="rwc") as con:
			pass
	with connect() as con:
		cur = con.cursor()
		for st in statements:
			cur.execute(st)


def main():
	initialize()


if __name__ == "__main__":
	main()
