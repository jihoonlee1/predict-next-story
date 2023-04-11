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


def merge_title_body(title, body):
	content = title + " " + body
	content = re.sub(r"\n+", " ", content).strip()
	return content


def positive_data(cur, sentence0, sentence1, labels, root_incident_ids):
	for root_incident_id, in root_incident_ids:
		cur.execute("SELECT title, body FROM incidents WHERE id = ?", (root_incident_id, ))
		root_title, root_body = cur.fetchone()
		root_content = merge_title_body(root_title, root_body)
		cur.execute("""
		SELECT
			incidents.title,
			incidents.body
		FROM incidents_relevant
		JOIN incidents ON incidents.id = incidents_relevant.child_incident_id
		WHERE incidents_relevant.root_incident_id = ?
		ORDER BY incidents_relevant.incident_order
		""", (root_incident_id, ))
		buildup_incidents = cur.fetchall()
		num_buildup_incidents = len(buildup_incidents)
		first_title, first_body = buildup_incidents[0]
		first_content = merge_title_body(first_title, first_body)
		sentence0.append(root_content)
		sentence1.append(first_content)
		labels.append(0)
		for i in range(num_buildup_incidents-1):
			target_title, target_body = buildup_incidents[i]
			next_title, next_body = buildup_incidents[i+1]
			target_content = merge_title_body(target_title, target_body)
			next_content = merge_title_body(next_title, next_body)
			sentence0.append(target_content)
			sentence1.append(next_content)
			labels.append(0)
	return (sentence0, sentence1, labels)


def negative_data(cur, sentence0, sentence1, labels, root_incident_ids):
	for root_incident_id, in root_incident_ids:
		cur.execute("SELECT title, body FROM incidents WHERE id = ?", (root_incident_id, ))
		root_title, root_body = cur.fetchone()
		root_content = merge_title_body(root_title, root_body)
		cur.execute("""
		SELECT
			incidents.title,
			incidents.body
		FROM incidents_irrelevant
		JOIN incidents ON incidents.id = incidents_irrelevant.child_incident_id
		WHERE incidents_irrelevant.root_incident_id = ?
		""", (root_incident_id, ))
		incidents_irrelevant = cur.fetchall()
		num_incidents_irrelevant = len(incidents_irrelevant)
		for title, body in incidents_irrelevant:
			irrelevant_content = merge_title_body(title, body)
			sentence0.append(root_content)
			sentence1.append(irrelevant_content)
			labels.append(1)
		for i in range(0, num_incidents_irrelevant-1):
			for j in range(i+1, num_incidents_irrelevant):
				target_title, target_body = incidents_irrelevant[i]
				next_title, next_body = incidents_irrelevant[j]
				target_content = merge_title_body(target_title, target_body)
				next_content = merge_title_body(next_title, next_body)
				sentence0.append(target_ontent)
				sentence1.append(next_content)
				labels.append(1)
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
		cur.execute("SELECT id FROM root_incidents")
		root_incident_ids = cur.fetchall()
		sentence0, sentence1, labels = [], [], []
		sentence0, sentence1, labels = positive_data(cur, sentence0, sentence1, labels, root_incident_ids)
		print(len(sentence0))
		sentence0, sentence1, labels = negative_data(cur, sentence0, sentence1, labels, root_incident_ids)
		print(len(sentence0))
		# inputs = tokenizer(sentence0, sentence1, return_tensors="pt", max_length=512, truncation=True, padding="max_length")

		# inputs["labels"] = torch.LongTensor([labels]).T
		# dataset = IncidentDataset(inputs)
		# dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
		# for epoch in range(epochs):
		# 	print(f"Epoch {epoch + 1}")
		# 	train_loop(dataloader, model, optimizer, loss_fn)
		# torch.save(model, "model.pth")


if __name__ == "__main__":
	main()

