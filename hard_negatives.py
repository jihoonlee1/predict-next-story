import database
from transformers import AutoTokenizer
import torch
import time


statement = """
CREATE TABLE IF NOT EXISTS hard_negatives(
	root_incident_id  INTEGER NOT NULL,
	child_incident_id INTEGER NOT NULL
)
"""
device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = torch.load("model.pth").to(device)
labels = torch.LongTensor([0]).to(device)


def predict(text1, text2):
	inputs = tokenizer(text1, text2, return_tensors="pt", truncation=True, max_length=512, padding="max_length")
	prediction = model(**inputs.to(device), labels=labels).logits[0]
	probability = torch.sigmoid(prediction)
	return probability.tolist()


def initialize():
	with database.connect():
		cur = con.cursor()
		cur.execute(statement)


def main():
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("""
		SELECT
			root_incidents.id,
			root_incidents.company_id,
			incidents.content
		FROM root_incidents
		JOIN incidents ON incidents.id = root_incidents.id
		""")
		root_incidents = cur.fetchall()
		for root_incident_id, root_company_id, root_content, in root_incidents:
			print(f"Parent: {root_content}")
			print("")
			cur.execute("""
			SELECT
				incidents.id,
				incidents.content
			FROM incidents_relevant
			JOIN incidents ON incidents.id = incidents_relevant.child_incident_id
			WHERE incidents_relevant.company_id != ?
			""", (root_company_id, ))
			rows = cur.fetchall()
			for child_incident_id, child_content, in rows:
				yes, no = predict(root_content, child_content)
				if yes > no:
					print(child_content)
					print(yes, no)
			print("--------------------------")





if __name__ == "__main__":
	main()