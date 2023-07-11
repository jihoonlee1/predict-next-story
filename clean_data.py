import database
import re


with database.connect() as con:
	cur = con.cursor()
	cur.execute("SELECT id, content FROM roots")
	for root_id, content in cur.fetchall():
		content = content.replace("```text", "")
		content = content.replace("```", "")
		content = content.replace("---", "")
		content = re.sub(r"\n+", "\n", content)
		content = content.strip()
		cur.execute("UPDATE roots SET content = ? WHERE id = ?", (content, root_id))
	con.commit()
