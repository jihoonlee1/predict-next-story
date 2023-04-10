import database
import json


def main():
	with database.connect() as con:
		cur = con.cursor()
		with open("forbes.txt") as f:
			data = json.load(f)["tabledata"]
			for company in data:
				cur.execute("SELECT ifnull(max(id)+1, 0) FROM companies")
				company_id, = cur.fetchone()
				company_name = company["organizationName"]
				try:
					description = company["description"]
				except:
					description = None
				industry = company["industry"]
				country = company["country"]
				revenue = company["revenue"]
				profits = company["profits"]
				assets = company["assets"]
				market_value = company["marketValue"]
				cur.execute("INSERT INTO companies VALUES(?,?,?,?,?,?,?,?,?)",
					(company_id, company_name, description, industry, country, revenue, profits, assets, market_value))
			con.commit()


if __name__ == "__main__":
	main()
