import database


def main():
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT id, name FROM companies")
		all_companies = cur.fetchall()
		num_companies = len(all_companies)
		for company_id, company_name in all_companies:
			cur.execute("SELECT 1 FROM incidents WHERE company_id = ?", (company_id, ))
			if cur.fetchone() is None:
				print(company_id, company_name)


if __name__ == "__main__":
	main()
