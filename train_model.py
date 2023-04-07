import database
from transformers import AutoTokenizer, BertForNextSentencePrediction, logging
import torch


logging.set_verbosity_error()
learning_rate = 1e-3
batch_size = 8
epochs = 3
device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)


with database.connect() as con:
	cur = con.cursor()
	cur.execute("""
	SELECT
		central_articles.company_id,
		companies.name,
		events.central_article_id,
		central_articles.title,
		central_articles.body,
		events.id,
		events.is_relevant
	FROM events
	JOIN central_articles ON central_articles.id = events.central_article_id
	JOIN companies ON companies.id = central_articles.company_id
	""")
	events = cur.fetchall()
	incidents_bag = []
	for company_id, company_name, central_article_id, central_article_title, central_article_body, event_id, is_relevant in events:
		print(company_name, event_id, is_relevant)
		central_article_content = central_article_title + " " + central_article_body[:500]
		cur.execute("""
		SELECT
			chatgpt_generated_incidents.id,
			chatgpt_generated_incidents.content,
			event_incident.story_order
		from event_incident
		JOIN chatgpt_generated_incidents ON chatgpt_generated_incidents.id = event_incident.incident_id
		WHERE event_incident.event_id = ?
		""", (event_id, ))
		rows = cur.fetchall()
		for incident_id, incident_content, story_order in rows:
			print(event_id, incident_id, story_order)
		break