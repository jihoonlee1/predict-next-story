import database
import re


def main():
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT id, content FROM chatgpt_generated_incidents")
		incidents = cur.fetchall()
		for incident_id, content in incidents:
			content = re.sub(r"Story [0-9][0-9]?: ", "", content)
			content = re.sub(r"Summary: ", "", content)
			cur.execute("BEGIN TRANSACTION")
			cur.execute("UPDATE chatgpt_generated_incidents SET content = ? WHERE id = ?", (content, incident_id))
			cur.execute("COMMIT TRANSACTION")


if __name__ == "__main__":
	main()