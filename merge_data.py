import database


def main():
	with database.connect("classification.sqlite") as con0:
		cur0 = con0.cursor()
		with database.connect("temp.sqlite") as con1:
			cur1 = con1.cursor()
			cur1.execute("SELECT id, content, company_id FROM incidents")
			incidents = cur1.fetchall()
			for old_id, content, company_id in incidents:
				old_root_id = None
				old_class_id = None
				old_soft_hard_pos_neg = None
				cur1.execute("SELECT 1 FROM root_incidents WHERE id = ?", (old_id, ))
				test0 = cur1.fetchone()
				if test0 is not None:
					old_root_id = old_id
				cur1.execute("SELECT soft_hard_pos_neg FROM classifications WHERE child_incident_id = ?", (old_id, ))
				test1 = cur1.fetchone()
				if test1 is not None:
					old_class_id = old_id
					old_soft_hard_pos_neg, = test1
				cur0.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
				new_id, = cur0.fetchone()
				cur0.execute("INSERT INTO incidents VALUES(?,?,?)", (new_id, content, company_id))
				if old_root_id is not None:
					cur0.execute("INSERT INTO root_incidents VALUES(?,?)", (new_id, company_id))
				if old_class_id is not None and old_soft_hard_pos_neg is not None:
					cur0.execute("SELECT id FROM root_incidents WHERE company_id = ? ORDER BY id DESC LIMIT 1", (company_id, ))
					root_id, = cur0.fetchone()
					cur0.execute("INSERT INTO classifications VALUES(?,?,?,?)", (root_id, new_id, company_id, old_soft_hard_pos_neg))
			con0.commit()


if __name__ == "__main__":
	main()
