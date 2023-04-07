import database
import chatgpt
import re


def clean(content):
	content = re.sub(r"[0-9](\.|\)+)", "", content)
	content = re.sub(r"\n+", " ", content).strip()
	return content


def main():
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT * FROM companies")
		companies = cur.fetchall()
		for company_id, company_name in companies:
			cur.execute("SELECT id, title FROM central_articles WHERE company_id = ?", (company_id, ))
			central_articles = cur.fetchall()
			for central_id, central_title in central_articles:
				question_followup= f'Come up with ten potential follow up headlines and summaries to "{central_title}" and make sure to include {company_name} in it.'
				question_non_followup = f'Come up with ten potential headlines and summaries that are not relevant to "{central_title}" and make sure to include {company_name} in it.'
				response = chatgpt.ask(question_non_followup)
				answers = response.split("\n\n")
				for answer in answers:
					answer = clean(answer)
					print(answer)
				break


if __name__ == "__main__":
	main()
