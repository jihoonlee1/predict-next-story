import database
import random
import re


def _delete_useless(con, cur):
	cur.execute("SELECT id, content FROM root_children_negative0 ORDER BY length(content) LIMIT 100")
	for root_id, content in cur.fetchall():
		print(content)


def _check_alias(con, cur):
	cur.execute("SELECT id, company_id, content FROM roots ORDER BY company_id")
	for root_id, company_id, root_content in cur.fetchall():
		cur.execute("SELECT name FROM companies WHERE id = ?", (company_id, ))
		company_name, = cur.fetchone()
		alias = [company_name]
		cur.execute("SELECT alias FROM company_alias WHERE company_id = ?", (company_id, ))
		for item, in cur.fetchall():
			alias.append(item)
		alias.sort(key=len, reverse=True)
		alias_str = "|".join(alias)
		cur.execute("SELECT id, content FROM root_children_positive0 WHERE root_event_id = ? AND company_id = ?", (root_id, company_id))
		for child_id, child_content in cur.fetchall():
			found = re.findall(rf"({alias_str})", child_content.lower(), flags=re.IGNORECASE)
			if not found:
				print(child_content)
				print(company_name, company_id, child_id)
				print(alias_str)
				print("----------------")



def _prep_negative1(con, cur):
	cur.execute("SELECT DISTINCT root_event_id FROM root_event_positive0")
	for root_event_id, in cur.fetchall():
		cur.execute("SELECT company_id FROM root_events WHERE id = ?", (root_event_id, ))
		company_id, = cur.fetchone()
		cur.execute("SELECT name FROM companies WHERE id = ?", (company_id, ))
		company_name, = cur.fetchone()
		cur.execute("SELECT name FROM companies WHERE id != ?", (company_id, ))
		other_company_names = cur.fetchall()
		other_company_name, = other_company_names[random.randint(0, len(other_company_names)-1)]
		alias = [company_name]
		cur.execute("SELECT alias FROM company_alias WHERE company_id = ?", (company_id, ))
		for item, in cur.fetchall():
			alias.append(item)
		alias.sort(key=len, reverse=True)
		alias_str = "|".join(alias)

		cur.execute("SELECT child_event_id FROM root_event_positive0 WHERE root_event_id = ?", (root_event_id, ))
		for child_event_id, in cur.fetchall():
			cur.execute("SELECT content FROM events WHERE id = ?", (child_event_id, ))
			child_content, = cur.fetchone()
			child_content = re.sub(rf"({alias_str})", other_company_name, child_content)
			cur.execute("SELECT ifnull(max(id)+1, 0) FROM events_negative1")
			new_event_id, = cur.fetchone()
			cur.execute("INSERT INTO events_negative1 VALUES(?,?,?)", (new_event_id, company_id, child_content))
			cur.execute("INSERT INTO root_event_negative1 VALUES(?,?,?)", (root_event_id, new_event_id, company_id))
		con.commit()


def _prep_negative2(con, cur):
	cur.execute("SELECT DISTINCT root_event_id FROM root_event_positive0")
	for root_event_id, in cur.fetchall():
		cur.execute("SELECT company_id FROM events WHERE id = ?", (root_event_id, ))
		company_id, = cur.fetchone()
		cur.execute("SELECT id FROM events WHERE company_id != ?", (company_id, ))
		diff_comp_events = cur.fetchall()
		num_diff_comp_events = len(diff_comp_events)
		samples = random.sample(range(0, num_diff_comp_events-1), 5)
		for randint in samples:
			diff_event_id, = diff_comp_events[randint]
			cur.execute("INSERT INTO root_event_negative2 VALUES(?,?,?)", (root_event_id, diff_event_id, company_id))
	con.commit()


def _prep_negative3(con, cur):
	cur.execute("SELECT DISTINCT root_event_id FROM root_event_positive0")
	for root_event_id, in cur.fetchall():
		print(root_event_id)
		cur.execute("SELECT company_id FROM events WHERE id = ?", (root_event_id, ))
		company_id, = cur.fetchone()
		cur.execute("SELECT name FROM companies WHERE id = ?", (company_id, ))
		company_name, = cur.fetchone()
		alias = [company_name]
		cur.execute("SELECT alias FROM company_alias WHERE company_id = ?", (company_id, ))
		for item, in cur.fetchall():
			alias.append(item)
		alias.sort(key=len, reverse=True)
		alias_str = "|".join(alias)

		replacements = []
		temp = set()
		cur.execute("SELECT child_event_id FROM root_event_positive0 WHERE root_event_id = ?", (root_event_id, ))
		child_event_ids = cur.fetchall()
		for child_event_id, in child_event_ids:
			cur.execute("SELECT content FROM events WHERE id = ?", (child_event_id, ))
			child_content, = cur.fetchone()
			child_doc = nlp(child_content)
			for entity in child_doc.ents:
				entity_text = re.sub(rf"({alias_str})", "", entity.text).strip()
				if entity_text != "":
					temp.add(entity_text)
		temp = sorted(temp, key=len)
		for item in temp:
			randint_person = random.randint(0, LEN_PERSON-1)
			randint_norp = random.randint(0, LEN_NORP-1)
			randint_fac = random.randint(0, LEN_FAC-1)
			randint_org = random.randint(0, LEN_ORG-1)
			randint_gpe = random.randint(0, LEN_GPE-1)
			randint_loc = random.randint(0, LEN_LOC-1)
			randint_product = random.randint(0, LEN_PRODUCT-1)
			randint_event = random.randint(0, LEN_EVENT-1)
			randint_work_of_art = random.randint(0, LEN_WORK_OF_ART-1)
			randint_law = random.randint(0, LEN_LAW-1)
			randint_language = random.randint(0, LEN_LANGUAGE-1)
			randint_date = random.randint(0, LEN_DATE-1)
			randint_time = random.randint(0, LEN_TIME-1)
			randint_percent = random.randint(0, LEN_PERCENT-1)
			randint_money = random.randint(0, LEN_MONEY-1)
			randint_quantity = random.randint(0, LEN_QUANTITY-1)
			randint_ordinal = random.randint(0, LEN_ORDINAL-1)
			randint_cardinal = random.randint(0, LEN_CARDINAL-1)
			ent_doc = nlp(item)
			entities = ent_doc.ents
			if not entities:
				continue
			entity_name = entities[0].text
			entity_label = entities[0].label_
			if entity_label == "PERSON":
				replacements.append([entity_name, PERSON[randint_person], "PERSON"])
			elif entity_label == "NORP":
				replacements.append([entity_name, NORP[randint_norp], "NORP"])
			elif entity_label == "FAC":
				replacements.append([entity_name, FAC[randint_fac], "FAC"])
			elif entity_label == "ORG":
				replacements.append([entity_name, ORG[randint_org], "ORG"])
			elif entity_label == "GPE":
				replacements.append([entity_name, GPE[randint_gpe], "GPE"])
			elif entity_label == "LOC":
				replacements.append([entity_name, LOC[randint_loc], "LOC"])
			elif entity_label == "PRODUCT":
				replacements.append([entity_name, PRODUCT[randint_product], "PRODUCT"])
			elif entity_label == "EVENT":
				replacements.append([entity_name, EVENT[randint_event], "EVENT"])
			elif entity_label == "WORK_OF_ART":
				replacements.append([entity_name, WORK_OF_ART[randint_work_of_art], "WORK_OF_ART"])
			elif entity_label == "LAW":
				replacements.append([entity_name, LAW[randint_law], "LAW"])
			elif entity_label == "LANGUAGE":
				replacements.append([entity_name, LANGUAGE[randint_language], "LANGUAGE"])
			elif entity_label == "DATE":
				replacements.append([entity_name, DATE[randint_date], "DATE"])
			elif entity_label == "TIME":
				replacements.append([entity_name, TIME[randint_time], "TIME"])
			elif entity_label == "PERCENT":
				replacements.append([entity_name, PERCENT[randint_percent], "PERCENT"])
			elif entity_label == "MONEY":
				replacements.append([entity_name, MONEY[randint_money], "MONEY"])
			elif entity_label == "QUANTITY":
				replacements.append([entity_name, QUANTITY[randint_quantity], "QUANTITY"])
			elif entity_label == "ORDINAL":
				replacements.append([entity_name, ORDINAL[randint_ordinal], "ORDINAL"])
			elif entity_label == "CARDINAL":
				replacements.append([entity_name, CARDINAL[randint_cardinal], "CARDINAL"])
		len_replacements = len(replacements)
		for i in range(len_replacements):
			is_isolated = True
			for j in range(i+1, len_replacements):
				if replacements[i][0] in replacements[j][0]:
					replacements[i][1] = replacements[j][1]
					replacements[i][2] = replacements[j][2]
		replacements = sorted(replacements, key=lambda x: len(x[0]), reverse=True)
		for child_event_id, in child_event_ids:
			can_insert = False
			cur.execute("SELECT content FROM events WHERE id = ?", (child_event_id, ))
			child_content, = cur.fetchone()
			for target, replacement, target_label in replacements:
				if target in child_content and target_label == "ORG":
					can_insert = True
			if can_insert:
				new_child_content = child_content
				for target, replacement, _ in replacements:
					new_child_content = new_child_content.replace(target, replacement)
				assert new_child_content != child_content
				cur.execute("SELECT ifnull(max(id)+1, 0) FROM events_negative3")
				new_event_id, = cur.fetchone()
				cur.execute("INSERT INTO events_negative3 VALUES(?,?,?)", (new_event_id, company_id, new_child_content))
				cur.execute("INSERT INTO root_event_negative3 VALUES(?,?,?)", (root_event_id, new_event_id, company_id))
		con.commit()


def main():
	with database.connect() as con:
		cur = con.cursor()
		_check_alias(con, cur)


if __name__ == "__main__":
	main()
