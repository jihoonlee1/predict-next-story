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


def main():
	cookie_fname = "cookie0.txt"
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT id, name FROM companies")
		companies = cur.fetchall()
		for idx, (company_id, company_name) in enumerate(companies):
			print(f"{idx}/2000 {company_name}")
			question = f'''Write 3 news scenarios about the company "{company_name}" on different subjects. Separate each stories with "Story: ".'''
			response = bing.ask(question, cookie_fname)
			roots = _split_response(response)
			for item in roots:
				cur.execute("SELECT ifnull(max(id)+1, 0) FROM roots")
				root_id, = cur.fetchone()
				cur.execute("INSERT INTO roots VALUES(?,?,?)", (root_id, company_id, item))
				con.commit()


if __name__ == "__main__":
	main()
