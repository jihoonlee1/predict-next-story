import database
import chatgpt
import re


def clean(content):
	content = re.sub(r"^[0-9][0-9]?(\.|\)?)", "", content)
	content = re.sub(r"\n+", " ", content).strip()
	return content


def insert_event(cur, question, central_article_id, company_id, is_relevant):
	response = chatgpt.ask(question)
	cur.execute("SELECT ifnull(max(id)+1, 0) FROM events")
	event_id, = cur.fetchone()
	cur.execute("BEGIN TRANSACTION")
	cur.execute("INSERT INTO events VALUES(?,?,?)", (event_id, central_article_id, is_relevant))
	cur.execute("COMMIT TRANSACTION")
	generated_incidents = [item for item in response.split("\n") if item != ""]
	while len(generated_incidents) != 20 and len(generated_incidents) != 10:
		response = chatgpt.ask(question)
		generated_incidents = [item for item in response.split("\n") if item != ""]
	if len(generated_incidents) == 20:
		temp = []
		for i in range(0, 20, 2):
			content = generated_incidents[i] + " " + generated_incidents[i+1]
			temp.append(content)
		generated_incidents = temp
	for idx, content in enumerate(generated_incidents):
		content = clean(content)
		print(content)
		cur.execute("SELECT ifnull(max(id)+1, 0) FROM chatgpt_generated_incidents")
		incident_id, = cur.fetchone()
		cur.execute("BEGIN TRANSACTION")
		cur.execute("INSERT INTO chatgpt_generated_incidents VALUES(?,?,?)", (incident_id, company_id, content))
		cur.execute("INSERT INTO event_incident VALUES(?,?,?)", (event_id, incident_id, idx))
		cur.execute("COMMIT TRANSACTION")


def main():
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT * FROM companies WHERE id >= ?", (56, ))
		companies = cur.fetchall()
		cur.execute("SELECT count(*) FROM central_articles")
		for company_id, company_name in companies:
			print(company_name)
			cur.execute("SELECT id, title, body FROM central_articles WHERE company_id = ?", (company_id, ))
			central_articles = cur.fetchall()
			num_central_articles = len(central_articles)
			for c_idx, (central_article_id, central_article_title, central_article_body) in enumerate(central_articles):
				if (company_id == 56):
					if central_article_id < 350:
						print(central_article_id)
						continue
				print(f"{c_idx}/{num_central_articles}")
				central_story = central_article_title + ". " + central_article_body[:500]
				question_followup = f'Come up with ten follow up stories to "{central_story}". Make sure each story has {company_name} in it and write the story as long as you can.'
				question_non_followup = f'Come up with ten stories that are not relevant to "{central_story}". Make sure each story has {company_name} in it and write the story as long as you can.'
				insert_event(cur, question_followup, central_article_id, company_id, 1)
				print("----------------")
				insert_event(cur, question_non_followup, central_article_id, company_id, 0)
				print("")


if __name__ == "__main__":
	main()