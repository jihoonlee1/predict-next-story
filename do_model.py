import database
import random
import torch
import transformers


device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
learning_rate = 5e-5
epochs = 4
batch_size = 8
tokenizer = transformers.AutoTokenizer.from_pretrained("bert-base-uncased")
model = transformers.BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
loss_fn = torch.nn.CrossEntropyLoss()


class IncidentDataset(torch.utils.data.Dataset):
	def __init__(self, encodings):
		self.encodings = encodings

	def __len__(self):
		return self.encodings.input_ids.shape[0]

	def __getitem__(self, idx):
		return {key: tensor[idx] for key, tensor in self.encodings.items()}


def positive_data(cur, sentence0, sentence1, labels, root_incident_ids):
	for root_incident_id, in root_incident_ids:
		cur.execute("SELECT content FROM incidents WHERE id = ?", (root_incident_id, ))
		prompt, = cur.fetchone()
		cur.execute("""
		SELECT
			incidents.content
		FROM classifications
		JOIN incidents ON incidents.id = classifications.child_incident_id
		WHERE root_incident_id = ? AND soft_hard_pos_neg = 0
		""", (root_incident_id, ))
		soft_pos = cur.fetchall()
		for content, in soft_pos:
			sentence0.append(prompt)
			sentence1.append(content)
			labels.append(0)
	return (sentence0, sentence1, labels)


def negative_data(cur, sentence0, sentence1, labels, root_incident_ids):
	for root_incident_id, in root_incident_ids:
		cur.execute("SELECT content FROM incidents WHERE id = ?", (root_incident_id, ))
		prompt, = cur.fetchone()
		cur.execute("""
		SELECT
			incidents.content
		FROM classifications
		JOIN incidents ON incidents.id = classifications.child_incident_id
		WHERE root_incident_id = ? AND soft_hard_pos_neg IN (2, 3)
		""", (root_incident_id, ))
		soft_hard_neg = cur.fetchall()
		for content, in soft_hard_neg:
			sentence0.append(prompt)
			sentence1.append(content)
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


def train_set(cur, root_ids):
	pass

def validate_set(cur, root_ids):
	pass

def test_set(cur, root_ids):
	pass


def calc_train_validate_end(total_length):
	train_end_idx = round(total_length * 0.8)
	rest = total_length - train_end_idx
	rest_half = round(rest * 0.5)
	validate_end_idx = train_end_idx + rest_half
	return (train_end_idx, validate_end_idx)

def main():
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT id FROM root_incidents")
		rows = cur.fetchall()
		root_incident_ids = []
		for root_id in rows:
			root_incident_ids.append(root_id)
		random.shuffle(root_incident_ids)

		num_root_incident_ids = len(root_incident_ids)
		train_end_idx, validate_end_idx = calc_train_validate_end(num_root_incident_ids)
		train_root_ids = root_incident_ids[:train_end_idx]
		validate_root_ids = root_incident_ids[train_end_idx:validate_end_idx]
		test_root_ids = root_incident_ids[validate_end_idx:]

		sent0_train, sent1_train, labels_train = positive_data(cur, [], [], [], train_root_ids)
		sent0_train, sent1_train, labels_train = negative_data(cur, sent0_train, sent1_train, labels_train, train_root_ids)

		sent0_validate, sent1_validate, labels_validate = positive_data(cur, [], [], [], validate_root_ids)
		sent0_validate, sent1_validate, labels_validate = negative_data(cur, sent0_validate, sent1_validate, labels_validate, validate_root_ids)

		sent0_test, sent1_test, labels_test = positive_data(cur, [], [], [], test_root_ids)
		sent0_test, sent1_test, labels_test = negative_data(cur, sent0_test, sent1_test, labels_test, test_root_ids)

		cur.execute("SELECT count(*) FROM incidents")
		print(cur.fetchone())

		print(num_root_incident_ids)
		print(len(sent0_train))
		print(len(sent0_validate))
		print(len(sent0_test))



		# sentence0, sentence1, labels = [], [], []  # 33% soft pos, 33% soft neg, 33% hard neg
		# sentence0, sentence1, labels = positive_data(cur, sentence0, sentence1, labels, root_incident_ids)
		# sentence0, sentence1, labels = negative_data(cur, sentence0, sentence1, labels, root_incident_ids)
		# inputs = tokenizer(sentence0, sentence1, return_tensors="pt", max_length=512, truncation=True, padding="max_length")
		# inputs["labels"] = torch.LongTensor([labels]).T
		# dataset = IncidentDataset(inputs)
		# dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
		# for epoch in range(epochs):
		# 	print(f"Epoch {epoch + 1}")
		# 	train_loop(dataloader, model, optimizer, loss_fn)
		# torch.save(model, "classification.pth")


if __name__ == "__main__":
	main()

