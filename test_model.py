import transformers
import torch


def predict(sent0, sent1, model, tokenizer, labels, device):
	inputs = tokenizer(sent0, sent1, return_tensors="pt", truncation=True, max_length=512, padding="max_length")
	pred = model(**inputs.to(device), labels=labels).logits[0]
	prob = torch.sigmoid(pred)
	return prob.tolist()


def main():
	device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
	ckp = torch.load("model-epoch-1.pth")
	tokenizer = transformers.AutoTokenizer.from_pretrained("bert-base-uncased")
	labels = torch.LongTensor([0]).to(device)
	model = transformers.BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
	model.load_state_dict(ckp["model_state_dict"])
	sent0 = "Russia invades Ukraine."
	sent1 = "Ukraine wins war against Russia."
	yes, no = predict(sent0, sent1, model, tokenizer, labels, device)
	print(yes, no)


if __name__ == "__main__":
	main()