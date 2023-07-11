import bing
import database
import queue
import threading
import utils
import re


QUEUE = queue.Queue()
NUM_COOKIES = utils.num_cookies()
NUM_COMPANIES_PER_COOKIE = 2
MAX_WORKERS = NUM_COMPANIES_PER_COOKIE * NUM_COOKIES


def _answers(text):
	temp = [item.strip() for item in re.split(r"(story:)", text, flags=re.IGNORECASE) if item != ""]
	temp = [item.strip() for item in temp if item != ""]
	len_temp = len(temp)
	result = []
	for i in range(len_temp-1):
		if temp[i].lower() == "story:" and temp[i+1].lower() != "story:":
			result.append(temp[i+1])
	return result


def _write_to_db():
	with database.connect() as con:
		cur = con.cursor()
		num_workers = MAX_WORKERS
		while True:
			if num_workers == 0:
				break
			item = QUEUE.get()
			if item is None:
				num_workers -= 1
				print(f"{num_workers}/{MAX_WORKERS} finished its job.")
			else:
				company_id, company_name = item[0]
				root_content = item[1]
				pos_container0 = item[2]
				pos_container1 = item[3]
				neg_container = item[4]
				cur.execute("SELECT ifnull(max(id)+1, 0) FROM roots")
				root_id, = cur.fetchone()
				cur.execute("INSERT INTO roots VALUES(?,?,?)", (root_id, company_id, root_content))

				for item in pos_container0:
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM root_children_positive0")
					child_id, = cur.fetchone()
					cur.execute("INSERT INTO root_children_positive0 VALUES(?,?,?,?)", (child_id, root_id, company_id, item))

				for item in pos_container1:
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM root_children_positive1")
					child_id, = cur.fetchone()
					cur.execute("INSERT INTO root_children_positive1 VALUES(?,?,?,?)", (child_id, root_id, company_id, item))

				for item in neg_container:
					cur.execute("SELECT ifnull(max(id)+1, 0) FROM root_children_negative0")
					child_id, = cur.fetchone()
					cur.execute("INSERT INTO root_children_negative0 VALUES(?,?,?,?)", (child_id, root_id, company_id, item))

				print(f"Inserting {company_name}")
				con.commit()


def root_question(company_name):
	return f'Write 5 news stories about "{company_name}" on different subject. Start each story with "Story: ".'


def pos_question0(company_name, root):
	return f'''Write 3 news stories about "{company_name}" that are considered as direct follow-ups to "{root}". Write each story from {company_name}'s perspective. Start each story with "Story: ". '''


def pos_question1(company_name, root):
	return f'''Write 3 news stories about "{company_name}" that are considered as direct follow-ups to "{root}". Write each story from a different company's perspective other than {company_name}. Start each story with "Story: ". '''


def neg_question(company_name, root):
	return f'Write 3 news stories about "{company_name}" that are irrelevant to "{root}". Start each story with "Story: ".'


def _scrap(company_id, company_name, cookie_fname):
	try:
		roots = _answers(bing.ask(root_question(company_name), cookie_fname))
		print(f"root: {len(roots)} {company_name}")
		for root in roots:
			data = []
			data.append((company_id, company_name))
			data.append(root)
			pos_container0 = []
			pos_container1 = []
			neg_container = []
			positives0 = _answers(bing.ask(pos_question0(company_name, root), cookie_fname))
			positives1 = _answers(bing.ask(pos_question1(company_name, root), cookie_fname))
			negatives = _answers(bing.ask(neg_question(company_name, root), cookie_fname))
			print(f"pos0: {len(positives0)} {company_name}")
			print(f"pos1: {len(positives1)} {company_name}")
			print(f"neg: {len(negatives)} {company_name}")
			for pos in positives0:
				pos_container0.append(pos)
			for pos in positives1:
				pos_container1.append(pos)
			for neg in negatives:
				neg_container.append(neg)
			data.append(pos_container0)
			data.append(pos_container1)
			data.append(neg_container)
			QUEUE.put(data)
	except Exception as e:
		print(f"Error: {cookie_fname}: {e}")
		QUEUE.put(None)
		return
	QUEUE.put(None)


def main():
	with database.connect() as con:
		write_thread = threading.Thread(target=_write_to_db)
		write_thread.start()

		cur = con.cursor()
		cur.execute("SELECT id, name FROM companies WHERE id NOT IN (SELECT DISTINCT company_id FROM roots)")
		companies = cur.fetchall()
		scrap_threads = []
		leftend = 0
		rightend = NUM_COMPANIES_PER_COOKIE

		for i in range(NUM_COOKIES):
			target_companies = companies[leftend:rightend]
			for company_id, company_name in target_companies:
				t = threading.Thread(target=_scrap, args=(company_id, company_name, f"cookie{i}.txt"))
				t.start()
				scrap_threads.append(t)
			leftend = rightend
			rightend = rightend + NUM_COMPANIES_PER_COOKIE

		for t in scrap_threads:
			t.join()

		write_thread.join()


if __name__ == "__main__":
	main()
