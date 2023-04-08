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
		cur.execute("""
		SELECT
			event_incident.event_id,
			event_incident.incident_id,
			event_incident.story_order,
			events.is_relevant,
			incidents.content
		FROM event_incident
		JOIN events ON events.id = event_incident.event_id
		JOIN incidents ON incidents.id = event_incident.incident_id
		""")
		for event_id, incident_id, story_order, is_relevant, content in cur.fetchall():
			incidents.append((event_id, is_relevant, incident_id, story_order, content))
		num_incidents = len(incidents)
		counter = 0
		while counter < num_incidents:
			start = random.randint(0, num_incidents-2)
			start_incident = incidents[start]
			cur.execute("SELECT count(*) FROM event_incident WHERE event_id = ?", (start_incident[0], ))
			incidents_count, = cur.fetchone()
			# if random.random() > 0.5:
			while (start_incident[1] == 0 and (incidents_count - 1) == start_incident[3]):
				start = random.randint(0, num_incidents-2)
				start_incident = incidents[start]
				cur.execute("SELECT count(*) FROM event_incident WHERE event_id = ?", (start_incident[0], ))
				incidents_count, = cur.fetchone()
			sentence1.append(start_incident[4])
			next_incident = incidents[start+1]
			sentence2.append(next_incident[4])
			labels.append(0)
			# else:

			# 	random_num = random.randint(0, num_incidents-1)
			# 	random_incident = incidents[random_num]
			# 	while (start_incident[4] == random_incident[4] and
			# 		((random_incident[0] == start_incident[0]) and
			# 		(random_incident[3] - start_incident[3] == 1) and
			# 		(start_incident[1] == 1 and random_incident[1] == 1))):
			# 		random_num = random.randint(0, num_incidents-1)
			# 		random_incident = incidents[random_num]
			# 	sentence1.append(start_incident[4])
			# 	sentence2.append(random_incident[4])
			# 	labels.append(1)
			counter += 1

		for i in range(5):
			print(sentence1[i])
			print("")
			print(sentence2[i])
			print(labels[i])
			print("---------------")

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