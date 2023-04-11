import database


def main():
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT count(*), company_id FROM incidents GROUP BY company_id")
		for count, company_id in cur.fetchall():
			if count != 30:
				print(company_id)


if __name__ == "__main__":
	main()
