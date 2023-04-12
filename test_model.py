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
	prob = torch.sigmoid(prediction)
	return prob.tolist()


def main():
	text1 = "Toyota creates new line of gourmet food products"
	text2 = "Toyota's Gourmet Foods Launch Party. Toyota will host a launch party to celebrate the release of its new line of gourmet foods. The event will feature samples of the new foods, as well as presentations from the chefs and food experts who developed them.0"
	yes, no = predict(text1, text2)
	print(yes, no)


if __name__ == "__main__":
	main()
