import database
import random
import re
import spacy


nlp = spacy.load("en_core_web_lg")


def _delete_useless(con, cur):
	cur.execute("SELECT id, content, length(content) FROM events ORDER BY length(content) LIMIT 100")
	for event_id, content, length in cur.fetchall():
		cur.execute("SELECT 1 FROM root_events WHERE id = ?", (event_id, ))
		if cur.fetchone() is not None:
			cur.execute("SELECT child_event_id FROM root_event_children WHERE root_event_id = ?", (event_id, ))
			for child_id, in cur.fetchall():
				cur.execute("DELETE FROM root_event_children WHERE child_event_id = ?", (child_id, ))
				cur.execute("DELETE FROM events WHERE id = ?", (child_id, ))
			cur.execute("DELETE FROM root_events WHERE id = ?", (event_id, ))
			cur.execute("DELETE FROM events WHERE id = ?", (event_id, ))
		cur.execute("SELECT 1 FROM root_event_children WHERE child_event_id = ?", (event_id, ))
		if cur.fetchone() is not None:
			cur.execute("DELETE FROM root_event_children WHERE child_event_id = ?", (event_id, ))
			cur.execute("DELETE FROM events WHERE id = ?", (event_id, ))
	con.commit()


def _separate_pos_neg(con, cur):
	cur.execute("SELECT * FROM root_event_children WHERE is_follow_up = 1")
	for root_id, child_id, company_id, _ in cur.fetchall():
		cur.execute("INSERT INTO root_event_positive0 VALUES(?,?,?)", (root_id, child_id, company_id))
	cur.execute("SELECT * FROM root_event_children WHERE is_follow_up = 0")
	for root_id, child_id, company_id, _ in cur.fetchall():
		cur.execute("INSERT INTO root_event_negative0 VALUES(?,?,?)", (root_id, child_id, company_id))
	con.commit()


def _check_alias(con, cur):
	cur.execute("SELECT company_id, id FROM root_events ORDER BY company_id")
	for company_id, root_event_id in cur.fetchall():
		cur.execute("SELECT content FROM events WHERE id = ?", (root_event_id, ))
		root_content, = cur.fetchone()
		cur.execute("SELECT name FROM companies WHERE id = ?", (company_id, ))
		company_name, = cur.fetchone()
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
			found = re.findall(rf"({alias_str})", child_content.lower(), flags=re.IGNORECASE)
			if not found:
				print(child_content)
				print(company_name, company_id, child_event_id)
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

		cur.execute("SELECT child_event_id FROM root_event_positive0 WHERE root_event_id = ?", (root_event_id, ))
		for child_event_id, in cur.fetchall():
			cur.execute("SELECT content FROM events WHERE id = ?", (child_event_id, ))
			child_content, = cur.fetchone()
			child_doc = nlp(child_content)
			replacements = set()
			for entity in child_doc.ents:
				entity_text = re.sub(rf"({alias_str})", "", entity.text).strip()
				if entity_text != "":
					replacements.add(entity_text)
			replacements = sorted(replacements, key=len, reverse=True)
			for item in replacements:
				item_doc = nlp(item)
				entities = item_doc.ents
				entity_text = entities[0].text
				entity_label = entities[0].label_
				print(entity_text, entity_label)
			print("----------")

		break


def main():
	with database.connect() as con:
		cur = con.cursor()
		_prep_negative3(con, cur)


if __name__ == "__main__":
	main()
