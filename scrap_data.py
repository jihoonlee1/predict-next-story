import database
import chatgpt
import time
import re


def answers(question):
	article_pattern = re.compile(r"Article *[0-9]*:", re.IGNORECASE)
	while True:
		try:
			response = chatgpt.ask(question)
			answers = [item.strip() for item in article_pattern.split(response0) if item != ""]
			return answers
		except:
			time.sleep(10)
			continue


def main():
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT id, name FROM companies WHERE id in (24,25,26,27,28,29,30,34,35,36,37,38,39,40,60)")
		for company_id, company_name in cur.fetchall():
			initial_question = f'''
			Write 10 news articles about {company_name}	on different topic.
			Make sure each article is about {company_name}.
			Make sure each article is more than 100 words.
			Separate each article with "Article: ".
			'''
			root_incidents = answers(initial_question)
			print(company_name, len(root_incidents))

			for counter, root_incident in enumerate(root_incidents):
				print(f"Root: {counter}")
				cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
				root_incident_id, = cur.fetchone()
				cur.execute("INSERT INTO incidents VALUES(?,?,?)", (root_incident_id, root_incident, company_id))
				cur.execute("INSERT INTO root_incidents VALUES(?,?)", (root_incident_id, company_id))

				soft_pos_question = f'''
				Write 20 news articles that are follow-up to "{root_incident}".
				Make sure each article is about {company_name}.
				Make sure each article is more than 100 words.
				Separate each article with "Article: ".
				'''
				soft_neg_question = f'''
				Write 20 news articles that are not follow-up to "{root_incident}".
				Make sure each article is about {company_name}.
				Make sure each article is more than 100 words.
				Separate each article with "Article: ".
				'''
				hard_neg_question0 = f'''
				Write 20 news articles that are similar to "{root_incident}".
				Make sure each article is not about {company_name}.
				Make sure each article is more than 100 words.
				Separate each article with "Article: ".
				'''

				soft_pos_incidents = answers(soft_pos_question)
				soft_neg_incidents = answers(soft_neg_question)
				hard_neg_incidents0 = answers(hard_neg_question0)

				print(f"Soft positive: {len(soft_pos_incidents)}")
				print(f"Soft negative: {len(soft_neg_incidents)}")
				print(f"Hard negative 0: {len(hard_neg_incidents0)}")

				# Soft pos - 0
				# Hard pos - 1
				# Soft neg - 2
				# Hard neg - 3

				for soft_pos_inc in soft_pos_incidents:
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
					soft_pos_inc_id, = cur.fetchone()
					cur.execute("INSERT INTO incidents VALUES(?,?,?)", (soft_pos_inc_id, soft_pos_inc, company_id))
					cur.execute("INSERT INTO classifications VALUES(?,?,?,?)", (root_incident_id, soft_pos_inc_id, company_id, 0))

				for soft_neg_inc in soft_neg_incidents:
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
					soft_neg_inc_id, = cur.fetchone()
					cur.execute("INSERT INTO incidents VALUES(?,?,?)", (soft_neg_inc_id, soft_neg_inc, company_id))
					cur.execute("INSERT INTO classifications VALUES(?,?,?,?)", (root_incident_id, soft_neg_inc_id, company_id, 2))

				for hard_neg_inc in hard_neg_incidents0:
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM incidents")
					hard_neg_inc_id, = cur.fetchone()
					cur.execute("INSERT INTO incidents VALUES(?,?,?)", (hard_neg_inc_id, hard_neg_inc, company_id))
					cur.execute("INSERT INTO classifications VALUES(?,?,?,?)", (root_incident_id, hard_neg_inc_id, company_id, 3))
				con.commit()
			print("------------------------")


if __name__ == "__main__":
	main()
