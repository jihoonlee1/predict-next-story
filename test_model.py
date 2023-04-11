from transformers import AutoTokenizer
import torch


device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = torch.load("model.pth").to(device)
labels = torch.LongTensor([0]).to(device)


def predict(text1, text2):
	inputs = tokenizer(text1, text2, return_tensors="pt", truncation=True, max_length=512, padding="max_length")
	prediction = model(**inputs, labels=labels).logits[0]
	prob = torch.sigmoid(prediction)
	return prob.tolist()


def main():
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT id FROM events WHERE company_id = ?", (8, ))
		for event_id, in cur.fetchall():
			cur.execute("""
			SELECT
				incidents.content
			FROM event_incident
			JOIN incidents ON incidents.id = event_incident.incident_id
			WHERE event_incident.event_id = ?
			ORDER BY event_incident.incident_order
			""")
			rows = cur.fetchall()
			text1, = rows[0]
			text2, = rows[1]
			print(text1)
			print(text2)
			yes, no = predict(text1, text2)
			print(yes, no)


if __name__ == "__main__":
	main()
