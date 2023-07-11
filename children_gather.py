import bing
import database
import re


split_pattern = re.compile(r"(story *:)", re.IGNORECASE)


def _split_response(text):
	result = []
	temp = [item.strip() for item in split_pattern.split(text)]
	num_temp = len(temp)
	for i in range(num_temp):
		if temp[i].lower().startswith("story"):
			result.append(temp[i+1])
	return result


def _pos_question(company_name, root_content):
	question = f'''Write 3 news scenarios about the company {company_name} where each of the scenario is a direct follow-up to "{root_content}". Separate each scenario with "Story: ".'''
	return question


def _neg_question(company_name, root_content):
	question = f'''Write 3 news scenarios about the company {company_name} where each of the scenario is irrelevant to "{root_content}". Separate each scenario with "Story: ".'''
	return question


def main():
	cookie_fname = "cookie0.txt"
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT id, company_id, content FROM roots")
		everything = cur.fetchall()
		len_everything = len(everything)
		for idx, (root_id, company_id, root_content) in enumerate(everything):
			if idx < 258:
				continue
			cur.execute("SELECT name FROM companies WHERE id = ?", (company_id, ))
			company_name, = cur.fetchone()
			print(f"{idx}/{len_everything} {company_name}")
			question = _neg_question(company_name, root_content)
			response = bing.ask(question, cookie_fname)
			items = _split_response(response)
			for item in items:
				cur.execute("SELECT ifnull(max(id)+1, 0) FROM children")
				child_id, = cur.fetchone()
				cur.execute("INSERT INTO children VALUES(?,?,?,?,?,?)", (child_id, root_id, company_id, item, 1, 1))
				con.commit()



if __name__ == "__main__":
	main()
