import database


statements = [
"""
CREATE TABLE incidents(
	id         INTEGER NOT NULL PRIMARY KEY,
	content    TEXT    NOT NULL,
	is_chatgpt INTEGER NOT NULL,
	company_id INTEGER NOT NULL
)
""",
"""
CREATE TABLE events(
	id             INTEGER NOT NULL PRIMARY KEY,
	start_incident INTEGER NOT NULL REFERENCES incidents(id),
	company_id     INTEGER NOT NULL
	is_relevant    INTEGER NOT NULL
)
""",
"""
CREATE TABLE event_incident(
	event_id       INTEGER NOT NULL REFERENCES events(id),
	incident_id    INTEGER NOT NULL REFERENCES incidents(id),
	incident_order INTEGER NOT NULL,
	PRIMARY KEY(event_id, incident_id)
)
"""
]




with database.connect() as con:
	cur = con.cursor()
	cur.execute("SELECT content, count(*) FROM incidents GROUP BY content ORDER BY count(*) DESC")
	total = 0
	for content, count in cur.fetchall():
		if count >= 4:
			cur.execute("SELECT id, company_id FROM incidents WHERE content = ?", (content, ))
			rows = cur.fetchall()
			for i in range(2):
				central_article = rows[i]
				cur.execute("SELECT event_id FROM event_incident WHERE incident_id = ?", (central_article[0], ))
				event_id, = cur.fetchone()
				cur.execute("SELECT incident_id FROM event_incident WHERE event_id = ? AND incident_id != ?", (event_id, central_article[0]))
				for incident_id, in cur.fetchall():
					total += 1
	print(total)