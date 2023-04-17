import contextlib
import json
import sqlite3


dbname = "classification2.sqlite"
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
	company_id INTEGER NOT NULL
)
""",
"""
CREATE TABLE classifications(
	root_incident_id   INTEGER NOT NULL,
	child_incident_id  INTEGER NOT NULL,
	company_id         INTEGER NOT NULL,
	soft_hard_pos_neg  INTEGER NOT NULL,
	PRIMARY KEY(root_incident_id, child_incident_id)
)
"""
]


def connect(database=dbname, mode="rw"):
	return contextlib.closing(sqlite3.connect(f"file:{database}?mode={mode}", uri=True))


def add_companies(cur):
	with open("forbes.txt") as f:
		data = json.load(f)["tabledata"]
		for company in data:
			cur.execute("SELECT ifnull(max(id)+1, 0) FROM companies")
			company_id, = cur.fetchone()
			company_name = company["organizationName"]
			try:
				description = company["description"]
			except:
				description = None
			industry = company["industry"]
			country = company["country"]
			revenue = company["revenue"]
			profits = company["profits"]
			assets = company["assets"]
			market_value = company["marketValue"]
			cur.execute("BEGIN TRANSACTION")
			cur.execute("INSERT INTO companies VALUES(?,?,?,?,?,?,?,?,?)",
				(company_id, company_name, description, industry, country, revenue, profits, assets, market_value))
			cur.execute("COMMIT TRANSACTION")


def main():
	for i in range(200):
		with connect(database=f"temp{i}.sqlite", mode="rwc") as con:
			cur = con.cursor()
			for st in statements:
				cur.execute(st)
			add_companies(cur)


if __name__ == "__main__":
	main()
