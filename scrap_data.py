import database
import chatgpt
import time
import re
import openai


def separate_response(question):
	while True:
		try:
			response = chatgpt.ask(question)
			pattern = re.compile(r"Article *[0-9]*:", re.IGNORECASE)
			answers = [item.strip() for item in pattern.split(response) if item != ""]
			return answers
		except openai.error.RateLimitError:
			time.sleep(5)
			continue


def title_body(content):
	temp = [item.strip() for item in content.split("\n") if item != ""]
	title = temp[0]
	body = "\n".join(temp[1:])
	return title, body


def main():
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT id, name FROM companies WHERE id > 6")
		for company_id, company_name in cur.fetchall():
			# Find 20 off topic root incidents about the same company.
			initial_question = f'20 news articles about {company_name} on different topic. Make sure each article is about {company_name}. Make sure each article is more than 100 words. Start each article with "Article: ".'
			root_incidents = separate_response(initial_question)
			print(f"Events: {len(root_incidents)} {company_name}")

			for root_incident in root_incidents:
				root_title, root_body = title_body(root_incident)
				cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
				root_incident_id, = cur.fetchone()
				cur.execute("INSERT INTO incidents VALUES(?,?,?,?)", (root_incident_id, root_title, root_body, company_id))
				cur.execute("INSERT INTO root_incidents VALUES(?,?)", (root_incident_id, company_id))

				# Find 10 follow up news articles per root incident.
				question_relevant = f'Write 10 follow up news articles to {root_incident} that build on each other. Make sure each article is about {company_name}. Make sure each article is more than 100 words. Start each article with "Article: ".'
				incidents_relevant = separate_response(question_relevant)
				print(f"Relevant news articles: {len(incidents_relevant)}")
				for incident_order, incident_relevant in enumerate(incidents_relevant):
					incident_relevant_title, incident_relevant_body = title_body(incident_relevant)
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
					incident_relevant_id, = cur.fetchone()
					cur.execute("INSERT INTO incidents VALUES(?,?,?,?)", (incident_relevant_id, incident_relevant_title, incident_relevant_body, company_id))
					cur.execute("INSERT INTO incidents_relevant VALUES(?,?,?,?)", (root_incident_id, incident_relevant_id, incident_order, company_id))

				# Find 10 irrelevant news articles per root incident.
				question_irrelevant = f'Write 10 irrelevant news articles to {root_incident}. Make sure each article is about {company_name}. Make sure the article is more than 100 words. Start each article with "Article: ".'
				incidents_irrelevant = separate_response(question_irrelevant)
				print(f"Irrelevant news articles: {len(incidents_irrelevant)}")
				for incident_irrelevant in incidents_irrelevant:
					incident_irrelevant_title, incident_irrelevant_body = title_body(incident_irrelevant)
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
					incident_irrelevant_id, = cur.fetchone()
					cur.execute("INSERT INTO incidents VALUES(?,?,?,?)", (incident_irrelevant_id, incident_irrelevant_title, incident_irrelevant_body, company_id))
					cur.execute("INSERT INTO incidents_irrelevant VALUES(?,?,?)", (root_incident_id, incident_irrelevant_id, company_id))
				con.commit()


if __name__ == "__main__":
	main()
