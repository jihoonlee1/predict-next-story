import database
import random
# from transformers import AutoTokenizer, BertForNextSentencePrediction, logging
# import torch


# logging.set_verbosity_error()
# learning_rate = 1e-3
# batch_size = 16
# epochs = 3
# device = "cuda" if torch.cuda.is_available() else "cpu"
# tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
# model = BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
# optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)


def get_training_data():
	with database.connect() as con:
		sentence1 = []
		sentence2 = []
		labels = []
		incidents = []
		cur = con.cursor()
		cur.execute("SELECT id, is_relevant FROM events")
		for event_id, is_relevant in cur.fetchall():
			cur.execute("""
			SELECT
				event_incident.event_id,
				event_incident.incident_id,
				event_incident.incident_order,
				incidents.content,
				incidents.is_chatgpt
			FROM event_incident
			JOIN incidents ON incidents.id = event_incident.incident_id
			WHERE event_incident.event_id = ?
			ORDER BY event_incident.incident_order
			""", (event_id, ))
			for _, incident_id, incident_order, content, is_chatgpt in cur.fetchall():
				if is_chatgpt == 0:
					content = content[:500]
				incidents.append((event_id, is_relevant, incident_id, incident_order, content, is_chatgpt))
		num_incidents = len(incidents)
		counter = 0

		while counter < 500:
			start = random.randint(0, num_incidents-2)
			start_incident = incidents[start]
			next_incident = incidents[start+1]
			cur.execute("SELECT count(*) FROM event_incident WHERE event_id = ?", (start_incident[0], ))
			incidents_count, = cur.fetchone()
			if random.random() > 0.5:
				while (start_incident[1] == 0 or (incidents_count - 1) == start_incident[3]):
					start = random.randint(0, num_incidents-2)
					start_incident = incidents[start]
					next_incident = incidents[start+1]
					cur.execute("SELECT count(*) FROM event_incident WHERE event_id = ?", (start_incident[0], ))
					incidents_count, = cur.fetchone()
				sentence1.append(start_incident[4])
				sentence2.append(next_incident[4])
				labels.append(0)
			else:
				if random.random() > 0.5:
					while start_incident[1] == 1:
						start = random.randint(0, num_incidents-2)
						start_incident = incidents[start]
						next_incident = incidents[start+1]
					sentence1.append(start_incident[4])
					sentence2.append(next_incident[4])
					labels.append(1)
				else:
					random_num = random.randint(0, num_incidents-1)
					random_incident = incidents[random_num]
					bigger_story = None
					smaller_story = None
					if start_incident[3] > random_incident[3]:
						bigger_story = start_incident[3]
						smaller_story = random_incident[3]
					elif start_incident[3] < random_incident[3]:
						bigger_story = random_incident[3]
						smaller_story = start_incident[3]
					while start_incident[0] == random_incident[0] and start_incident[1] == 1 and bigger_story - smaller_story == 1:
						random_num = random.randint(0, num_incidents-1)
						random_incident = incidents[random_num]
						if start_incident[3] > random_incident[3]:
							bigger_story = start_incident[3]
							smaller_story = random_incident[3]
						elif start_incident[3] < random_incident[3]:
							bigger_story = random_incident[3]
							smaller_story = start_incident[3]
					sentence1.append(start_incident[4])
					sentence2.append(random_incident[4])
					labels.append(1)
			counter += 1

		return (sentence1, sentence2, labels)

get_training_data()


# class IncidentDataset(torch.utils.data.Dataset):
# 	def __init__(self, encodings):
# 		self.encodings = encodings

# 	def __len__(self):
# 		return self.encodings.input_ids.shape[0]

# 	def __getitem__(self, idx):
# 		return {key: tensor[idx] for key, tensor in self.encodings.items()}


# def train_loop(dataloader, model, optimizer):
# 	for batch in dataloader:
# 		input_ids = batch["input_ids"].to(device)
# 		token_type_ids = batch["token_type_ids"].to(device)
# 		attention_mask = batch["attention_mask"].to(device)
# 		labels = batch["labels"].to(device)
# 		outputs = model(input_ids, token_type_ids=token_type_ids, attention_mask=attention_mask, labels=labels)
# 		loss = outputs.loss
# 		optimizer.zero_grad()
# 		loss.backward()
# 		optimizer.step()
# 		print(f"Loss: {loss.item():>7f}")


# def main():
# 	sentence1, sentence2, labels = get_training_data()
# 	num_dataset = len(labels)
# 	for epoch in range(epochs):
# 		print(f"Epoch {epoch}")
# 		inputs = tokenizer(sentence1, sentence2, return_tensors="pt", max_length=512, truncation=True, padding="max_length")
# 		inputs["labels"] = torch.LongTensor([labels]).T
# 		dataset = IncidentDataset(inputs)
# 		dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
# 		train_loop(dataloader, model, optimizer)
# 	torch.save(model, "model.pth")


# if __name__ == "__main__":
# 	main()
