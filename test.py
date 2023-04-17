import database


with database.connect(database="classification-temp.sqlite") as con:
	cur = con.cursor()
	cur.execute("SELECT child_incident_id FROM classifications WHERE soft_hard_pos_neg = 0")
	rows = cur.fetchall()
	num_rows = len(rows)
	for child_incident_id, in rows:
		print(child_incident_id)
		cur.execute("DELETE FROM incidents WHERE id = ?", (child_incident_id, ))
		cur.execute("DELETE FROM classifications WHERE child_incident_id = ?", (child_incident_id, ))
	con.commit()
