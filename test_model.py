import torch
from transformers import BertTokenizer, BertForNextSentencePrediction, logging
import re
import contextlib
import sqlite3


logging.set_verbosity_error()
device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
model = BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
checkpoint = torch.load("model_epoch2.pth")
model.load_state_dict(checkpoint["model_state_dict"])
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")


statements = [
"""
CREATE TABLE IF NOT EXISTS chains(
	id         INTEGER NOT NULL PRIMARY KEY,
	company_id TEXT    NOT NULL
)
""",
"""
CREATE TABLE IF NOT EXISTS chain_event(
	chain_id    INTEGER NOT NULL,
	event_id    INTEGER NOT NULL,
	event_order INTEGER NOT NULL,
	PRIMARY KEY(chain_id, event_id)
)
""",
"""
CREATE INDEX IF NOT EXISTS events_index0 ON events(company_id, timestamp, title, body)
"""
]


def connect(database="events.sqlite", mode="rw"):
	return contextlib.closing(sqlite3.connect("file:events.sqlite?mode=rw", uri=True))


def predict(sent1, sent2):
	inputs = tokenizer(sent1, sent2, return_tensors="pt", max_length=512, padding="max_length", truncation=True)
	pred = model(**inputs.to(device))
	return torch.sigmoid(pred.logits)[0].tolist()


def clean_text(text):
	text = re.sub(r"\n+", " ", text)
	text = text.strip()
	return text


def main():
	with connect() as con:
		cur = con.cursor()
		cur.execute("SELECT count(*), company_name, company_id FROM events GROUP BY company_id ORDER BY count(*) DESC")
		companies = cur.fetchall()
		num_companies = len(companies)
		for idx, (count, company_name, company_id) in enumerate(companies):
			if count > 2000:
				continue
			print(f"{idx}/{num_companies} company_name: {company_name} num_events: {count}")
			cur.execute("SELECT id, timestamp, title, body FROM events WHERE company_id = ? ORDER BY timestamp", (company_id, ))
			rows = cur.fetchall()
			num_rows = len(rows)
			for i in range(num_rows):
				chain = []
				start = i
				while True:
					done = True
					parent_id, parent_timestamp, parent_title, parent_body = rows[start]
					parent_body = clean_text(parent_body)
					chain.append(parent_id)
					for j in range(start+1, num_rows):
						target_id, target_timestamp, target_title, target_body = rows[j]
						target_body = clean_text(target_body)
						if target_timestamp == parent_timestamp:
							continue
						if target_timestamp - parent_timestamp > 5259600000:
							continue
						cur.execute("SELECT 1 FROM chain_event WHERE event_id = ?", (target_id, ))
						if cur.fetchone() is not None:
							continue
						yes, no = predict(parent_body, target_body)
						if yes >= 0.95:
							done = False
							start = j
							break
					if done:
						print(chain)
						if len(chain) > 1:
							cur.execute("SELECT ifnull(max(id)+1, 0) FROM chains")
							chain_id, = cur.fetchone()
							cur.execute("INSERT INTO chains VALUES(?,?)", (chain_id, company_id))
							for idx, item in enumerate(chain):
								cur.execute("INSERT INTO chain_event VALUES(?,?,?)", (chain_id, item, idx))
							con.commit()
						break



if __name__ == "__main__":
	main()