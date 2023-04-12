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
	probability = torch.sigmoid(prediction)
	return probability.tolist()


def main():
	text1 = "Ukraine invades Korea."
	text2 = "Russia wins."
	no, yes = predict(text1, text2)
	print(no, yesl)



if __name__ == "__main__":
	main()
