import bottle
import torch
import json
from transformers import BertTokenizer, BertForNextSentencePrediction, logging


logging.set_verbosity_error()
device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
model = BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
checkpoint = torch.load("model_epoch2.pth")
model.load_state_dict(checkpoint["model_state_dict"])
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")


@bottle.get("/static/<filepath:path>")
def server_static(filepath):
	return bottle.static_file(filepath, root="../static")


@bottle.route("/")
@bottle.view("index")
def _route():
	pass


@bottle.post("/api/predict")
def _post():
	sent1 = bottle.request.forms.get("sentence1")
	sent2 = bottle.request.forms.get("sentence2")
	inputs = tokenizer(sent1, sent2, return_tensors="pt", max_length=512, padding="max_length", truncation=True)
	pred = model(**inputs.to(device))
	bottle.response.content_type = "application/json; charset=utf=8"
	result = torch.sigmoid(pred.logits)[0].tolist()
	return json.dumps(result)


def main():
	bottle.run(port=8000, reloader=True, debug=True)


if __name__ == "__main__":
	main()