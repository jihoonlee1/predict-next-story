import re
import sqlite3
import contextlib
import bing


topics = [
"Land Use and Biodiversity",
"Energy Use and Greenhouse Gas Emissions",
"Emissions to Air",
"Degradation & Contamination (Land)",
"Discharges and Releases (Water)",
"Environmental Impact of Products",
"Carbon Impact of Products",
"Water Use",
"Discrimination & Harassment",
"Forced Labour",
"Freedom of Association",
"Health and Safety",
"Labour Relations",
"Other labour standards",
"Child Labour",
"False or Deceptive Marketing",
"Data Privacy and Security",
"Services Quality and Safety",
"Anti-competitive Practices",
"Product Quality and Safety",
"Customer Management",
"Conflicts with Indigenous Communities",
"Conflicts with Local Communities",
"Water Rights",
"Land Rights",
"Arms Export",
"Controversial Weapons",
"Sanctions",
"Involvement With Entities Violating Human Rights",
"Occupied Territories/Disputed Regions",
"Social Impact of products",
"Media Ethics",
"Access to Basic Services",
"Employees - Other Human Rights Violations",
"Society - Other Human Rights Violations",
"Local Community - Other",
"Taxes avoidance/evasion",
"Accounting Irregularities and Accounting Fraud",
"Lobbying and Public Policy",
"Insider Trading",
"Bribery and Corruption",
"Remuneration",
"Shareholder disputes/rights",
"Board composition",
"Corporate Governance - other",
"Intellectual Property",
"Animal Welfare",
"Resilience",
"Business Ethics - Other"
]


topics = "\n".join(topics)
print(topics)

def _question(article, topics=topics):
	question = f'''This is a reading comprehension task. Given an article, for each proper noun, label sentiment towards the topics from the provided list below. Only use topics from the provided list. Sentiment should be obvious to the reader, and capture the author’s intent. Only draw from the information in the article. For each proper noun, provide the exact text span of its first mention, then list the positive and negative sentiments. Do not list neutral sentiments. For example:

Topics: {topics}

Example Article: Monday, the Associated Press. Ford Motor Company fires 200 workers in order to invest in electric vehicles following their green initiative.

Example Labels:

Monday:
Positive Topics:
Negative Topics:

the Associated Press:
Positive Topics:
Negative Topics:

Ford Motor Company:
Positive Topics:
Environmental Impact of Products
Carbon Impact of Products
Negative Topics:
Labour Relations

Annotated the following article: {article}
	'''
	return question


def open_database(database="partial.sqlite", mode="rw"):
	return contextlib.closing(sqlite3.connect(f"file:{database}?mode={mode}", uri=True))


def main():
	with open_database() as con:
		cur = con.cursor()
		event_id = 47177
		cur.execute("SELECT title, body FROM events WHERE id = ?", (event_id, ))
		title, body = cur.fetchone()
		title = re.sub(r"\n+", " ", title)
		body = re.sub(r"\n+", " ", body)
		content = title + " " + body
		print(content)
		print("")
		cur.execute("SELECT DISTINCT pronoun FROM event_pronoun_label WHERE event_id = ?", (event_id, ))
		for pronoun, in cur.fetchall():
			print(f"pronoun: {pronoun}")
			cur.execute("SELECT label, pos_neg FROM event_pronoun_label WHERE event_id = ? AND pronoun = ?", (event_id, pronoun))
			for label, pos_neg in cur.fetchall():
				if pos_neg == 0:
					print(f"pos_label: {label}")
				else:
					print(f"neg_label: {label}")
			print("---------")


