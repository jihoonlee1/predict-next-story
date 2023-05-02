import database


with database.connect() as con:
	cur = con.cursor()
	string = '"K" Line'
	cur.execute("SELECT id, content FROM root_children_positive0 WHERE content LIKE ?", (f"%{string}%", ))
	for event_id, content in cur.fetchall():
		content = content.replace('"K" Line', "K Line")
		content = content.replace('"K" LINE', "K Line")
		cur.execute("UPDATE root_children_positive0 SET content = ? WHERE id = ?", (content, event_id))
	con.commit()
