import database


with database.connect() as con:
	cur = con.cursor()
	cur.execute("SELECT id FROM root_incidents")
	for root_incident_id, in cur.fetchall():
		cur.execute("SELECT title FROM incidents WHERE id = ?", (root_incident_id, ))
		root_title, = cur.fetchone()
		print(f"Parent: {root_title}")
		print("Relevant: ")
		cur.execute("""
		SELECT
			incidents.title
		FROM incidents_relevant
		JOIN incidents ON incidents.id = incidents_relevant.child_incident_id
		WHERE incidents_relevant.root_incident_id = ?
		""", (root_incident_id, ))
		relevants = cur.fetchall()
		for item, in relevants:
			print(item)
		print("")
		print("Irrelevant: ")
		cur.execute("""
		SELECT
			incidents.title
		FROM incidents_irrelevant
		JOIN incidents ON incidents.id = incidents_irrelevant.child_incident_id
		WHERE incidents_irrelevant.root_incident_id = ?
		""", (root_incident_id, ))
		irrelevants = cur.fetchall()
		for item, in irrelevants:
			print(item)
		print("\n\n\n")
