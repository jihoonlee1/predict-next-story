from transformers import AutoTokenizer, logging
import database
import torch
import time
import re


logging.set_verbosity_error()
device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = torch.load("classification.pth").to(device)
labels = torch.LongTensor([1]).to(device)


def predict(sent1, sent2):
	inputs = tokenizer(sent1, sent2, return_tensors="pt", max_length=512, truncation=True, padding="max_length")
	pred = model(**inputs.to(device), labels=labels).logits[0]
	prob = torch.sigmoid(pred)
	return prob.tolist()


def main():
	sent1 = "Russia invades Ukraine."
	sent2 = "Ukraine wins the war against Russia."
	yes, no = predict(sent1, sent2)
	print(yes, no)
	# with database.connect("/home/jihoon/code/next-sentence/incidents.sqlite") as con:
	# 	cur = con.cursor()
	# 	cur.execute("SELECT central_article_title, central_article_body FROM incidents WHERE company_id = ? ORDER BY central_article_timestamp_unix_ms", ("1007910258", ))
	# 	incidents = cur.fetchall()
	# 	num_incidents = len(incidents)
	# 	start = 0
	# 	yes, no = 0, 0
	# 	while start < num_incidents:
	# 		parent_title, parent_body = incidents[start]
	# 		parent_title = re.sub(r"\n+", " ", parent_title).strip()
	# 		parent_body = re.sub(r"\n+", " ", parent_body).strip()
	# 		parent_content = parent_title + " " + parent_body
	# 		print(parent_content)
	# 		print("")
	# 		found = False
	# 		for i in range(start+1, num_incidents):
	# 			child_title, child_body = incidents[i]
	# 			child_title = re.sub(r"\n+", " ", child_title).strip()
	# 			child_body = re.sub(r"\n+", " ", child_body).strip()
	# 			child_content = child_title + " " + child_body
	# 			yes, no = predict(parent_content, child_content)
	# 			if yes > 0.9:
	# 				print(yes, no)
	# 				found = True
	# 				start = i
	# 				break
	# 		if not found:
	# 			start = start + 1


if __name__ == "__main__":
	main()
