import torch
from transformers import BertTokenizer, BertForNextSentencePrediction, logging
import re
import database

logging.set_verbosity_error()
device = torch.device("cpu") if torch.cuda.is_available() else torch.device("cpu")
model = BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
checkpoint = torch.load("model_epoch1.pth")
model.load_state_dict(checkpoint["model_state_dict"])
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")


def predict(sent1, sent2):
	inputs = tokenizer(sent1, sent2, return_tensors="pt", max_length=512, padding="max_length", truncation=True)
	pred = model(**inputs.to(device))
	return torch.sigmoid(pred.logits)[0].tolist()


def main():
	with database.connect("/home/jihoon/code/topic-impact/incidents-for-comparison.sqlite") as con:
		cur = con.cursor()
		cur.execute("SELECT DISTINCT company_id FROM incidents")
		for company_id, in cur.fetchall():
			cur.execute("""
			SELECT
				articles.title,
				articles.body
			FROM incidents
			JOIN articles ON articles.article_id = incidents.central_article_id
			WHERE incidents.company_id = ?
			ORDER BY articles.nate_timestamp_unix_ms
			""", (company_id,))
			central_articles = []
			for title, body in cur.fetchall():
				title = re.sub(r"\n+", " ", title).strip()
				body = re.sub(r"\n+", " ", body).strip()
				content = title + " " + body
				central_articles.append(content)
			
			start = central_articles[0]
			rest = central_articles[1:]
			for content in rest:
				yes, no = predict(start, content)
				if yes > 0.9:
					print(start)
					print("")
					print(content)
					print("")
					break
			print("")
			print("")
			print("----------------")


if __name__ == "__main__":
	main()
