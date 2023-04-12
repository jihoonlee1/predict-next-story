import database
from transformers import AutoTokenizer, BertForNextSentencePrediction, logging
import torch
import time


logging.set_verbosity_error()
device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
# model = torch.load("model.pth").to(device)
labels = torch.LongTensor([1]).to(device)


def predict(text1, text2):
	inputs = tokenizer(text1, text2, return_tensors="pt", truncation=True, max_length=512, padding="max_length")
	prediction = model(**inputs.to(device), labels=labels).logits[0]
	probability = torch.sigmoid(prediction)
	yes, no = probability.tolist()
	return {
		"yes": yes,
		"no": no
	}


def main():
	text1 = "Russia invades Ukraine."
	text2 = "America wins."
	print(text1)
	print(text2)
	print(predict(text1, text2))



if __name__ == "__main__":
	main()
