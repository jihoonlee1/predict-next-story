import database


with database.connect(database="classification-temp.sqlite") as con:
	cur = con.cursor()
	for i in range(200):
		print(f"temp{i}.sqlite")
		with database.connect(database=f"temp{i}.sqlite") as con2:
			cur2 = con2.cursor()
			cur2.execute("""
			SELECT
				root_incidents.id,
				incidents.content,
				incidents.company_id
			FROM root_incidents
			JOIN incidents ON incidents.id = root_incidents.id
			""")
			rows = cur2.fetchall()
			for root_id, root_content, company_id in rows:
				cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
				new_root_id, = cur.fetchone()
				cur.execute("INSERT INTO incidents VALUES(?,?,?)", (new_root_id, root_content, company_id))
				cur.execute("INSERT INTO root_incidents VALUES(?,?)", (new_root_id, company_id))
				cur2.execute("""
				SELECT
					incidents.content
				FROM classifications
				JOIN incidents ON incidents.id = classifications.child_incident_id
				WHERE root_incident_id = ?
				""", (root_id, ))
				for child_content, in cur2.fetchall():
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
					new_child_id, = cur.fetchone()
					cur.execute("INSERT INTO incidents VALUES(?,?,?)", (new_child_id, child_content, company_id))
					cur.execute("INSERT INTO classifications VALUES(?,?,?,?)", (new_root_id, new_child_id, company_id, 0))
				con.commit()
