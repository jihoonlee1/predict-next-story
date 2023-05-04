import database
import random
import re


def _all_proper_nouns():
	with open("proper_nouns.txt", "r") as f:
		proper_nouns = [item.strip() for item in f.readlines()]
		proper_nouns = [item for item in proper_nouns if item != ""]
	return proper_nouns


def _remove_unwanted(con, cur):
	cur.execute("SELECT id, length(content) FROM roots")
	roots = cur.fetchall()
	cur.execute("SELECT id, length(content) FROM root_children_positive0")
	positives = cur.fetchall()
	cur.execute("SELECT id, length(content) FROM root_children_negative0")
	negatives = cur.fetchall()
	for root_id, length in roots:
		if length == 0:
			cur.execute("DELETE FROM root_children_positive0 WHERE root_id = ?", (root_id, ))
			cur.execute("DELETE FROM root_children_negative0 WHERE root_id = ?", (root_id, ))
			cur.execute("DELETE FROM roots WHERE id = ?", (root_id, ))
	for pos_id, length in positives:
		if length == 0:
			cur.execute("DELETE FROM root_children_positive0 WHERE id = ?", (pos_id, ))
	for neg_id, length in negatives:
		if length == 0:
			cur.execute("DELETE FROM root_children_negative0 WHERE id = ?", (neg_id, ))
	con.commit()


def _prep_negative1(con, cur):
	cur.execute("SELECT id, company_id FROM roots")
	for root_id, company_id in cur.fetchall():
		print(root_id)
		cur.execute("SELECT name FROM companies WHERE id = ?", (company_id, ))
		company_name, = cur.fetchone()
		company_name = company_name.replace("(", "\\(").replace(")", "\\)").replace(".", "\\.")
		alias = [company_name]
		cur.execute("SELECT name FROM companies WHERE id != ?", (company_id, ))
		other_companies = cur.fetchall()
		cur.execute("SELECT alias FROM company_alias WHERE company_id = ?", (company_id, ))
		for item, in cur.fetchall():
			alias.append(item)
		alias.sort(key=len, reverse=True)
		alias_str = "|".join(alias)
		cur.execute("SELECT content FROM root_children_positive0 WHERE root_id = ? AND company_id = ?", (root_id, company_id))
		positives = cur.fetchall()
		for content, in positives:
			other_company_name, = other_companies[random.randint(0, len(other_companies)-1)]
			content = re.sub(rf"{alias_str}", other_company_name, content)
			cur.execute("SELECT ifnull(max(id)+1, 0) FROM root_children_negative1")
			new_id, = cur.fetchone()
			cur.execute("INSERT INTO root_children_negative1 VALUES(?,?,?,?)", (new_id, root_id, company_id, content))
	con.commit()


def _prep_negative2(con, cur):
	all_proper_nouns = _all_proper_nouns()
	num_all_proper_nouns = len(all_proper_nouns)
	cur.execute("SELECT id, company_id FROM roots")
	for root_id, company_id in cur.fetchall():
		print(root_id)
		cur.execute("SELECT name FROM companies WHERE id = ?", (company_id, ))
		company_name, = cur.fetchone()
		company_name = company_name.replace("(", "\\(").replace(")", "\\)").replace(".", "\\.")
		alias = [company_name]
		cur.execute("SELECT alias FROM company_alias WHERE company_id = ?", (company_id, ))
		for item, in cur.fetchall():
			alias.append(item)
		alias.sort(key=len, reverse=True)
		alias_str = "|".join(alias)
		cur.execute("SELECT content FROM root_children_positive0 WHERE root_id = ? AND company_id = ?", (root_id, company_id))
		positives = cur.fetchall()
		for content, in positives:
			distinct_prop_nouns = set()
			prop_nouns = re.findall(r"\[\[([a-zA-Z0-9_ &.()]*)\]\]", content)
			for item in prop_nouns:
				distinct_prop_nouns.add(item)
			distinct_prop_nouns = sorted(distinct_prop_nouns, key=len)
			num_distinct_prop_nouns = len(distinct_prop_nouns)
			for i in range(num_distinct_prop_nouns):
				for j in range(i+1, num_distinct_prop_nouns):
					try:
						if distinct_prop_nouns[i] in distinct_prop_nouns[j]:
							distinct_prop_nouns.remove(distinct_prop_nouns[i])
					except:
						continue
			for item in distinct_prop_nouns:
				is_company = re.findall(rf"{alias_str}", item)
				if is_company:
					distinct_prop_nouns.remove(item)
			if not distinct_prop_nouns:
				continue
			for item in distinct_prop_nouns:
				random_proper_noun = all_proper_nouns[random.randint(0, num_all_proper_nouns-1)]
				while re.findall(rf"{alias_str}", random_proper_noun):
					random_proper_noun = all_proper_nouns[random.randint(0, num_all_proper_nouns-1)]
				content = re.sub(rf"\[\[{item}\]\]", f"[[{random_proper_noun}]]", content)
			cur.execute("SELECT ifnull(max(id)+1, 0) FROM root_children_negative2")
			new_id, = cur.fetchone()
			cur.execute("INSERT INTO root_children_negative2 VALUES(?,?,?,?)", (new_id, root_id, company_id, content))
	con.commit()


if __name__ == "__main__":
	with database.connect() as con:
		cur = con.cursor()
		# _remove_unwanted(con, cur)
		# _prep_negative1(con, cur)
		_prep_negative2(con, cur)
