import database
import random
from transformers import AutoTokenizer, BertForNextSentencePrediction, logging
import torch


logging.set_verbosity_error()
learning_rate = 1e-3
batch_size = 8
epochs = 3
device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
loss_fn = torch.nn.CrossEntropyLoss()


def get_starting_incident(cur, num_incidents):
	random_number = random.randint(0, num_incidents-1)
	cur.execute("SELECT id FROM incidents WHERE ROWID= ?", (random_number, ))
	incident_id, = cur.fetchone()
	cur.execute("SELECT event_id FROM event_incident WHERE incident_id = ?", (incident_id, ))
	event_id, = cur.fetchone()
	cur.execute("SELECT count(*) FROM event_incident WHERE event_id = ?", (event_id, ))
	incident_count, = cur.fetchone()
	cur.execute("""
	SELECT
		incidents.content,
		incidents.is_chatgpt,
		events.id,
		events.is_relevant,
		event_incident.incident_order
	FROM event_incident
	JOIN incidents ON incidents.id = event_incident.incident_id
	JOIN events ON events.id = event_incident.event_id
	WHERE event_incident.incident_id = ?
	""", (incident_id, ))
	content, is_chatgpt, event_id, is_relevant, incident_order = cur.fetchone()
	if is_chatgpt == 0:
		content = content[:500]
	return (incident_id, incident_count, content, is_chatgpt, event_id, is_relevant, incident_order)


def get_related_incident(cur, event_id, incident_order):
	cur.execute("""
	SELECT
		incidents.content
	FROM event_incident
	JOIN incidents ON incidents.id = event_incident.incident_id
	WHERE event_incident.event_id = ? AND event_incident.incident_order > ?
	ORDER BY event_incident.incident_order
	""", (event_id, incident_order))
	related_incidents = cur.fetchall()
	num_related_incidents = len(related_incidents)
	random_number = random.randint(0, num_related_incidents-1)
	content, = related_incidents[random_number]
	return content


def get_random_incident(cur, event_id):
	cur.execute("""
	SELECT
		incidents.content
	FROM event_incident
	JOIN incidents ON incidents.id = event_incident.incident_id
	WHERE event_incident.event_id != ?
	""", (event_id, ))
	rows = cur.fetchall()
	num_rows = len(rows)
	random_number = random.randint(0, num_rows-1)
	content, = rows[random_number]
	return content


def get_training_data():
	with database.connect() as con:
		sentence1 = []
		sentence2 = []
		labels = []
		cur = con.cursor()
		cur.execute("SELECT count(*) FROM incidents")
		num_incidents, = cur.fetchone()
		print(num_incidents)
		counter = 0
		while counter < 20000:
			print(counter)
			incident_id, incident_count, content, is_chatgpt, event_id, is_relevant, incident_order = get_starting_incident(cur, num_incidents)
			if random.random() > 0.5:
				while is_relevant == 0 or incident_count - incident_order == 1:
					incident_id, incident_count, content, is_chatgpt, event_id, is_relevant, incident_order = get_starting_incident(cur, num_incidents)
				related_incident = get_related_incident(cur, event_id, incident_order)
				sentence1.append(content)
				sentence2.append(related_incident)
				labels.append(0)
			else:
				random_content = get_random_incident(cur, event_id)
				sentence1.append(content)
				sentence2.append(random_content)
				labels.append(1)
			counter += 1
		return (sentence1, sentence2, labels)


class IncidentDataset(torch.utils.data.Dataset):
	def __init__(self, encodings):
		self.encodings = encodings

	def __len__(self):
		return self.encodings.input_ids.shape[0]

	def __getitem__(self, idx):
		return {key: tensor[idx] for key, tensor in self.encodings.items()}


def train_loop(dataloader, model, optimizer, loss_fn):
	for batch in dataloader:
		input_ids = batch["input_ids"].to(device)
		token_type_ids = batch["token_type_ids"].to(device)
		attention_mask = batch["attention_mask"].to(device)
		labels = batch["labels"].to(device)
		outputs = model(input_ids, token_type_ids=token_type_ids, attention_mask=attention_mask, labels=labels)
		# loss = outputs.loss
		loss = loss_fn(outputs.logits, labels.squeeze_())
		optimizer.zero_grad()
		loss.backward()
		optimizer.step()
		print(f"Loss: {loss.item():>7f}")


def main():
	sentence1, sentence2, labels = get_training_data()
	num_dataset = len(labels)
	for epoch in range(epochs):
		print(f"Epoch {epoch}")
		inputs = tokenizer(sentence1, sentence2, return_tensors="pt", max_length=512, truncation=True, padding="max_length")
		inputs["labels"] = torch.LongTensor([labels]).T
		dataset = IncidentDataset(inputs)
		dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
		train_loop(dataloader, model, optimizer, loss_fn)
	torch.save(model, "model.pth")


if __name__ == "__main__":
	main()
