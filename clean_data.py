import database


def main():
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT id, name FROM companies")
		all_companies = cur.fetchall()
		for company_id, company_name in all_companies:
			cur.execute("")

if __name__ == "__main__":
	main()
