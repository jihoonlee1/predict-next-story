import database
from transformers import AutoTokenizer
import torch
import time


device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = torch.load("model.pth").to(device)
labels = torch.LongTensor([0]).to(device)


def predict(text1, text2):
	inputs = tokenizer(text1, text2, return_tensors="pt", truncation=True, max_length=512, padding="max_length")
	prediction = model(**inputs.to(device), labels=labels).logits[0]
	return prediction


def main():
	with database.connect(database="database1.sqlite") as con:
		cur = con.cursor()
		cur.execute("SELECT root_incidents.id, incidents.title, incidents.body FROM root_incidents JOIN incidents ON incidents.id = root_incidents.id")
		for root_incident_id, root_title, root_body in cur.fetchall():
			root_content = root_title + " " + root_body
			print(f"Root: {root_content}")
			print("")
			cur.execute("SELECT title, body FROM incidents WHERE id != ?", (root_incident_id, ))
			for child_title, child_body in cur.fetchall():
				child_content = child_title + " " + child_body
				pred = predict(root_content, child_content)
				print(f"Child: {child_content}")
				print(pred)
				print("")
				time.sleep(2)
			break



if __name__ == "__main__":
	main()
