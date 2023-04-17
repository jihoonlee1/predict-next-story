import database
import chatgpt
import time
import re
import sys


def answers(question):
	article_pattern = re.compile(r"Article *[0-9]*:", re.IGNORECASE)
	while True:
		try:
			response = chatgpt.ask(question)
			answers = [item.strip() for item in article_pattern.split(response) if item != ""]
			return answers
		except Exception as e:
			print(e)
			continue


def scrap(dbname, leftend, rightend):
	print(dbname, leftend, rightend)
	with database.connect(database=dbname) as con:
		cur = con.cursor()
		cur.execute("SELECT id, name FROM companies WHERE id >= ? AND id <= ?", (leftend, rightend))
		for company_id, company_name in cur.fetchall():
			initial_question = f'''
			Write 5 news articles about {company_name} on different topic.
			Make sure each article is about {company_name}.
			Make sure each article is more than 50 words.
			Separate each article with "Article: ".
			'''
			root_incidents = answers(initial_question)
			print(company_name, len(root_incidents))

			for counter, root_incident in enumerate(root_incidents):
				print(f"Root: {root_incident}")
				cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
				root_incident_id, = cur.fetchone()
				cur.execute("INSERT INTO incidents VALUES(?,?,?)", (root_incident_id, root_incident, company_id))
				cur.execute("INSERT INTO root_incidents VALUES(?,?)", (root_incident_id, company_id))

				soft_pos_question = f'''
				Write 5 news articles that are follow-ups to "{root_incident}".
				Make sure the keywords from the parent article are in each of the follow-up article.
				Make sure each article is about {company_name}.
				Make sure each article is more than 50 words.
				Separate each article with "Article: ".
				'''
				soft_neg_question = f'''
				Write 5 news articles that are not follow-ups to "{root_incident}".
				Make sure each article is about {company_name}.
				Make sure each article is more than 50 words.
				Separate each article with "Article: ".
				'''
				hard_neg_question = f'''
				Write 5 articles that are similar to "{root_incident}".
				Make sure each article is not about {company_name}.
				Make sure each article is more than 50 words.
				Separate each article with "Article: ".
				'''

				soft_pos_incidents = answers(soft_pos_question)
				soft_neg_incidents = answers(soft_neg_question)
				hard_neg_incidents = answers(hard_neg_question)

				print(f"Soft positive: {len(soft_pos_incidents)}")
				print(f"Soft negative: {len(soft_neg_incidents)}")
				print(f"Hard negative: {len(hard_neg_incidents)}")
				# Soft pos - 0
				# Hard pos - 1
				# Soft neg - 2
				# Hard neg - 3

				for soft_pos_inc in soft_pos_incidents:
					print(f"Soft pos: {soft_pos_inc}")
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
					soft_pos_inc_id, = cur.fetchone()
					cur.execute("INSERT INTO incidents VALUES(?,?,?)", (soft_pos_inc_id, soft_pos_inc, company_id))
					cur.execute("INSERT INTO classifications VALUES(?,?,?,?)", (root_incident_id, soft_pos_inc_id, company_id, 0))

				for soft_neg_inc in soft_neg_incidents:
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
					soft_neg_inc_id, = cur.fetchone()
					cur.execute("INSERT INTO incidents VALUES(?,?,?)", (soft_neg_inc_id, soft_neg_inc, company_id))
					cur.execute("INSERT INTO classifications VALUES(?,?,?,?)", (root_incident_id, soft_neg_inc_id, company_id, 2))

				for hard_neg_inc in hard_neg_incidents:
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
					hard_neg_inc_id, = cur.fetchone()
					cur.execute("INSERT INTO incidents VALUES(?,?,?)", (hard_neg_inc_id, hard_neg_inc, company_id))
					cur.execute("INSERT INTO classifications VALUES(?,?,?,?)", (root_incident_id, hard_neg_inc_id, company_id, 3))

				con.commit()
			print("------------------------")
