import database
import chatgpt
import re


def separate_response(question):
	while True:
		try:
			response = chatgpt.ask(question)
			answers = [item.strip() for item in re.split(r"Article *[0-9]*: ", response) if item != ""]
			return answers
		except:
			continue


def main():
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT id, name FROM companies")
		for company_id, company_name in cur.fetchall():
			initial_question = f'5 news articles about {company_name} on different topic. Start each article with "Article: ".'
			different_events = separate_response(initial_question)
			for event in different_events:
				cur.execute("SELECT ifnull(max(id)+1, 0) FROM events")
				event_id, = cur.fetchone()
				cur.execute("INSERT INTO events VALUES(?,?)", (event_id, company_id))
				cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
				parent_incident_id, = cur.fetchone()
				cur.execute("INSERT INTO incidents VALUES(?,?,?)", (parent_incident_id, event, company_id))
				cur.execute("INSERT INTO event_incident VALUES(?,?,?)", (event_id, parent_incident_id, 0))
				last_question = f'5 follow-up news articles to {event} that build on each other. Start each article with "Article: ".'
				stories = separate_response(last_question)
				for story_order, story in enumerate(stories):
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
					incident_id, = cur.fetchone()
					cur.execute("INSERT INTO incidents VALUES(?,?,?)", (incident_id, story, company_id))
					cur.execute("INSERT INTO event_incident VALUES(?,?,?)", (event_id, incident_id, story_order+1))
					con.commit()

