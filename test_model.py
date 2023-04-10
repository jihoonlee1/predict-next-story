from transformers import AutoTokenizer,BertForNextSentencePrediction 
import torch
import database
import re


device = "cuda" if torch.cuda.is_available() else "cpu"
#model = torch.load("model.pth").to(device)
model = BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
labels = torch.LongTensor([0]).to(device)


def predict_next(text1, text2):
	inputs = tokenizer(text1, text2, return_tensors="pt", max_length=512, truncation=True, padding="max_length")
	prediction = model(**inputs.to(device), labels=labels).logits[0]
	probability = torch.sigmoid(prediction)
	return probability.tolist()


def main():
	with database.connect("incidents.sqlite") as con:
		cur = con.cursor()
		company_id = "1030264212"
		cur.execute("SELECT central_article_title, central_article_body FROM incidents WHERE company_id = ? ORDER BY central_article_timestamp_unix_ms", (company_id, ))
		incidents = cur.fetchall()
		num_incidents = len(incidents)
		print(num_incidents)
		start = 0
		while start < num_incidents - 1:
			found = False
			parent_title, parent_body = incidents[start]
			parent_content = parent_title + " " + parent_body[:500]
			print(f"{start}, {parent_title}")
			for i in range(start+1, num_incidents):
				child_title, child_body = incidents[i]
				child_content = child_title + " " + child_body[:500]
				is_next, not_next = predict_next(parent_content, child_content)
				if is_next >= 0.95:
					start = i
					found = True
					break
			if not found:
				print("-----------------")
				start += 1


def test():
	text1 = "Hi my name is justin"
	text2 = "hey Suha nice to meet you!"
	yes, no = predict_next(text1, text2)
	print(yes, no)


if __name__ == "__main__":
	test()
