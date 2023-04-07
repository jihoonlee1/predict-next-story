import database
import re


def main():
	with database.connect(database="incidents.sqlite") as con0:
		cur0 = con0.cursor()
		with database.connect() as con1:
			cur1 = con1.cursor()
			cur0.execute("""
			SELECT
				companies.id,
				companies.name,
				count(*)
			FROM incidents
			JOIN companies on companies.id = incidents.company_id
			GROUP BY incidents.company_id
			ORDER BY count(*) DESC
			""")
			companies = cur0.fetchall()
			for company_id, company_name, company_incidents_count in companies:
				incident_insertion_count = 0
				print(f"{company_id} {company_name} {company_incidents_count}")
				do_company = input("Yes or no? (y/n) ")
				if do_company == "y":
					cur1.execute("SELECT ifnull(max(id)+1, 0) FROM companies")
					new_company_id, = cur1.fetchone()
					cur1.execute("INSERT INTO companies VALUES(?,?)", (new_company_id, company_name))
					cur0.execute("SELECT central_article_title, central_article_body, central_article_timestamp_unix_ms FROM incidents WHERE company_id = ?", (company_id, ))
					incidents = cur0.fetchall()
					num_incidents = len(incidents)
					for idx, (title, body, timestamp) in enumerate(incidents):
						if incident_insertion_count == 10:
							print("Move onto the next company!")
							break
						title = re.sub(r"\n+", " ", title).strip()
						body = re.sub(r"\n+", " ",body).strip()
						print(f"{idx}/{num_incidents}")
						print(title)
						do_incident = input("Insert this incident? (y/n) ")
						if do_incident == "y":
							incident_insertion_count += 1
							cur1.execute("SELECT ifnull(max(id)+1, 0) FROM central_articles")
							new_central_article_id, = cur1.fetchone()
							cur1.execute("INSERT INTO central_articles VALUES(?,?,?,?,?)", (new_central_article_id, new_company_id, title, body, timestamp))
							con1.commit()
							cur1.execute("SELECT count(*) FROM central_articles")
							num_current_central_articles, = cur1.fetchone()
							print(f"Central articles in database count: {num_current_central_articles}")
						else:
							continue
				else:
					continue


if __name__ == "__main__":
	main()
