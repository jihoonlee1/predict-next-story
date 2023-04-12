import database
from transformers import AutoTokenizer, BertForNextSentencePrediction, logging
import torch
import time


logging.set_verbosity_error()
device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
# model = BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
model = torch.load("model.pth").to(device)
labels = torch.LongTensor([1]).to(device)


def predict(text1, text2):
	inputs = tokenizer(text1, text2, return_tensors="pt", truncation=True, max_length=512, padding="max_length")
	pred = model(**inputs.to(device), labels=labels).logits[0]
	prob = torch.sigmoid(pred)
	return prob.tolist()


def main():
	print(yes, no)
	# with database.connect() as con:
	# 	cur = con.cursor()
	# 	cur.execute("SELECT id FROM companies")
	# 	for company_id, in cur.fetchall():
	# 		cur.execute("SELECT content FROM incidents WHERE company_id = ?", (company_id, ))
	# 		contents = cur.fetchall()
	# 		num_contents = len(contents)
	# 		start = 0
	# 		while True:
	# 			prompt, = contents[start]
	# 			print(prompt)
	# 			print("---------------")
	# 			for i in range(start+1, num_contents):
	# 				next_sent, = contents[i]
	# 				yes, no = predict(prompt, next_sent)
	# 				if yes > 0.95:
	# 					start = i
	# 					time.sleep(3)
	# 					break


if __name__ == "__main__":
	main()
