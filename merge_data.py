import database


def main():
	with database.connect("classification.sqlite") as con0:
		cur0 = con0.cursor()
		for i in range(31):
			with database.connect(f"temp{i}.sqlite") as con1:
				cur1 = con1.cursor()
				cur1.execute("""
				SELECT
					root_incidents.id,
					root_incidents.company_id,
					incidents.content
				FROM root_incidents
				JOIN incidents ON incidents.id = root_incidents.id
				""")
				roots = cur1.fetchall()
				for root_id, company_id, root_content in roots:
					cur0.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
					new_root_id, = cur0.fetchone()
					cur0.execute("INSERT INTO incidents VALUES(?,?,?)", (new_root_id, root_content, company_id))
					cur0.execute("INSERT INTO root_incidents VALUES(?,?)", (new_root_id, company_id))
					cur1.execute("""
					SELECT
						incidents.content,
						classifications.soft_hard_pos_neg
					FROM classifications
					JOIN incidents ON incidents.id = classifications.child_incident_id
					WHERE classifications.root_incident_id = ?
					""", (root_id, ))
					childs = cur1.fetchall()
					for child_content, soft_hard_pos_neg in childs:
						cur0.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
						new_child_id, = cur0.fetchone()
						cur0.execute("INSERT INTO incidents VALUES(?,?,?)", (new_child_id, child_content, company_id))
						cur0.execute("INSERT INTO classifications VALUES(?,?,?,?)", (new_root_id, new_child_id, company_id, soft_hard_pos_neg))
				con0.commit()

if __name__ == "__main__":
	main()
