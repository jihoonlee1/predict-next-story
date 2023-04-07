import database
# from transformers import AutoTokenizer, BertForNextSentencePrediction, logging
# import torch


# logging.set_verbosity_error()
# learning_rate = 1e-3
# batch_size = 8
# epochs = 3
# device = "cuda" if torch.cuda.is_available() else "cpu"
# tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
# model = BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
# optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)


with database.connect() as con:
	cur = con.cursor()
	cur.execute("""
	SELECT
		central_articles.title,
		central_articles.body,
		events.id,
		events.is_relevant
	FROM events
	JOIN central_articles ON central_articles.id = events.central_article_id
	""")
	events = cur.fetchall()
	sentence1 = []
	sentence2 = []
	labels = []
	for central_article_title, central_article_body, event_id, is_relevant in events:
		central_article_content = central_article_title + " " + central_article_body[:500]
		cur.execute("""
		SELECT
			chatgpt_generated_incidents.content,
			event_incident.story_order
		FROM event_incident
		JOIN chatgpt_generated_incidents ON chatgpt_generated_incidents.id = event_incident.incident_id
		WHERE event_incident.event_id = ?
		""", (event_id, ))
		rows = cur.fetchall()
		num_rows = len(rows)
		for incident_content, story_order in rows:
			sentence1.append(central_article_content)
			sentence2.append(incident_content)
			if is_relevant == 1:
				labels.append(0)
			elif is_relevant == 0:
				labels.append(1)
		for i in range(num_rows):
			target_content, target_order = rows[i]
			for j in range(i+1, num_rows):
				candidate_content, candidate_order = rows[j]
				sentence1.append(target_content)
				sentence2.append(candidate_content)
				if is_relevant == 1:
					labels.append(0)
				elif is_relevant == 0:
					labels.append(1)
		break
	print(len(sentence1))
	print(len(sentence2))
	print(len(labels))
	print(sentence1[9])
	print(sentence2[9])
	print(labels[9])
