import database
import chatgpt
import time
import re
import openai


article_pattern = re.compile(r"Article *[0-9]*:", re.IGNORECASE)


def main():
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT id, name FROM companies")
		for company_id, company_name in cur.fetchall():
			# Find 20 off topic root incidents about the same company.
			initial_question = f'''
			Write 10 news articles about {company_name}	on different topic.
			Make sure each article is about {company_name}.
			Make sure each article is more than 100 words.
			Separate each article with "Article: ".
			'''
			response0 = chatgpt.ask(initial_question)
			root_incidents = [item.strip() for item in article_pattern.split(response0) if item != ""]
			print(company_name, len(root_incidents))
			for counter, root_incident in enumerate(root_incidents):
				print(counter)
				cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
				root_incident_id, = cur.fetchone()
				cur.execute("INSERT INTO incidents VALUES(?,?,?)", (root_incident_id, root_incident, company_id))
				cur.execute("INSERT INTO root_incidents VALUES(?,?)", (root_incident_id, company_id))
				good_question = f'''
				Write 20 news articles that could potentially be direct follow-up to "{root_incident}".
				Make sure each article is about {company_name}.
				Make sure each article is more than 100 words.
				Separate each article with "Article: ".
				'''
				bad_question = f'''
				Write 20 news articles that could potentially be follow-up, but is not direct follow-up to "{root_incident}".
				Make sure each article is about {company_name}.
				Make sure each article is more than 100 words.
				Separate each article with "Article: ".
				'''
				good_incidents = chatgpt.ask(good_question)
				good_incidents = [item.strip() for item in article_pattern.split(good_incidents) if item != ""]
				bad_incidents = chatgpt.ask(bad_question)
				bad_incidents = [item.strip() for item in article_pattern.split(bad_incidents) if item != ""]
				print(f"{len(good_incidents)} good incidents")
				print(f"{len(bad_incidents)} bad incidents")

				for good_incident in good_incidents:
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
					good_incident_id, = cur.fetchone()
					cur.execute("INSERT INTO incidents VALUES(?,?,?)", (good_incident_id, good_incident, company_id))
					cur.execute("INSERT INTO classifications VALUES(?,?,?,?)", (root_incident_id, good_incident_id, company_id, 1))

				for bad_incident in bad_incidents:
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
					bad_incident_id, = cur.fetchone()
					cur.execute("INSERT INTO incidents VALUES(?,?,?)", (bad_incident_id, bad_incident, company_id))
					cur.execute("INSERT INTO classifications VALUES(?,?,?,?)", (root_incident_id, bad_incident_id, company_id, 0))
				con.commit()
			print("------------------------")


if __name__ == "__main__":
	main()
