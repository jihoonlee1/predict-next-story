from transformers import AutoTokenizer, BertForNextSentencePrediction, logging
import database
import random
import re
import torch


logging.set_verbosity_error()
device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
learning_rate = 5e-5
epochs = 3
batch_size = 16
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
loss_fn = torch.nn.CrossEntropyLoss()


class IncidentDataset(torch.utils.data.Dataset):
	def __init__(self, encodings):
		self.encodings = encodings

	def __len__(self):
		return self.encodings.input_ids.shape[0]

	def __getitem__(self, idx):
		return {key: tensor[idx] for key, tensor in self.encodings.items()}


def positive_data(cur, sentence0, sentence1, labels):
	cur.execute("SELECT id FROM events")
	for event_id, in cur.fetchall():
		cur.execute("""
		SELECT
			incidents.content
		FROM event_incident
		JOIN incidents ON incidents.id = event_incident.incident_id
		WHERE event_incident.event_id = ?
		ORDER BY event_incident.incident_order
		""", (event_id, ))
		incidents = cur.fetchall()
		num_incidents = len(incidents)
		for i in range(num_incidents-1):
			start_incident, = incidents[i]
			next_incident, = incidents[i+1]
			start_incident = re.sub(r"\n+", " ", start_incident)
			next_incident = re.sub(r"\n+", " ", next_incident)
			sentence0.append(start_incident)
			sentence1.append(next_incident)
			labels.append(0)
	return (sentence0, sentence1, labels)


def negative_data(cur, sentence0, sentence1, labels, incidents_all, num_incidents_all):
	num_positives = len(sentence0)
	half_iteration = round(num_positives / 2)
	iteration = 0

	while iteration < num_positives:
		print(iteration)
		random_number = random.randint(0, num_incidents_all-1)
		target_incident_id, target_content = incidents_all[random_number]
		target_content = re.sub(r"\n+", " ", target_content)
		cur.execute("SELECT event_id FROM event_incident WHERE incident_id = ?", (target_incident_id, ))
		event_id, = cur.fetchone()  # grab event id of the random incident
		cur.execute("""
		SELECT
			incidents.content
		FROM event_incident
		JOIN incidents ON incidents.id = event_incident.incident_id
		WHERE event_incident.event_id != ?
		""", (event_id, ))
		unrelated_incidents = cur.fetchall()
		num_unrelated_incidents = len(unrelated_incidents)
		random_number = random.randint(0, num_unrelated_incidents-1)
		unrelated_content, = unrelated_incidents[random_number]
		unrelated_content = re.sub(r"\n+", " ", unrelated_content)
		random_num = random.randint(0, num_incidents_all-1)
		target_incident_id, target_company_id, target_content = incidents_all[random_num]
		target_content = re.sub(r"\n+", " ", target_content)
		cur.execute("SELECT event_id FROM event_incident WHERE incident_id = ?", (target_incident_id, ))
		target_event_id, = cur.fetchone()
		cur.execute("SELECT incident_id FROM event_incident WHERE company_id = ? AND event_id != ?", (target_company_id, target_event_id))
		rows = cur.fetchall()
		num_rows = len(rows)
		random_num = random.randint(0, num_rows-1)
		same_company_non_relevant_id, = rows[random_num]
		cur.execute("SELECT content FROM incidents WHERE id = ?", (same_company_non_relevant_id, ))
		next_content, = cur.fetchone()
		next_content = re.sub(r"\n+", " ", next_content)
		sentence0.append(target_content)
		sentence1.append(next_content)
		labels.append(1)
		iteration += 1
	return (sentence0, sentence1, labels)


def train_loop(dataloader, model, optimizer, loss_fn):
	for batch in dataloader:
		input_ids = batch["input_ids"].to(device)
		token_type_ids = batch["token_type_ids"].to(device)
		attention_mask = batch["attention_mask"].to(device)
		labels = batch["labels"].to(device)
		output = model(input_ids, token_type_ids=token_type_ids, attention_mask=attention_mask, labels=labels)
		loss = loss_fn(output.logits, labels.squeeze_())
		optimizer.zero_grad()
		loss.backward()
		optimizer.step()
		print(f"loss: {loss.item():>7f}")


def main():
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT id, company_id, content FROM incidents")
		incidents_all = cur.fetchall()
		num_incidents_all = len(incidents_all)
		sentence0, sentence1, labels = [], [], []
		sentence0, sentence1, labels = positive_data(cur, sentence0, sentence1, labels)
		sentence0, sentence1, labels = negative_data(cur, sentence0, sentence1, labels, incidents_all, num_incidents_all)
		print(len(sentence0))
		inputs = tokenizer(sentence0, sentence1, return_tensors="pt", max_length=512, truncation=True, padding="max_length")

		inputs["labels"] = torch.LongTensor([labels]).T
		dataset = IncidentDataset(inputs)
		dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
		for epoch in range(epochs):
			print(f"Epoch {epoch + 1}")
			train_loop(dataloader, model, optimizer, loss_fn)
		torch.save(model, "model.pth")


if __name__ == "__main__":
	main()

