import database
import torch
import random
import transformers


class IncidentDataset(torch.utils.data.Dataset):
	def __init__(self, encodings):
		self.encodings = encodings

	def __len__(self):
		return self.encodings.input_ids.shape[0]

	def __getitem__(self, idx):
		return {key: tensor[idx] for key, tensor in self.encodings.items()}


def get_all_root_incidents(cur):
	cur.execute("SELECT id FROM root_incidents")
	rows = cur.fetchall()
	root_incident_ids = []
	for root_id, in rows:
		root_incident_ids.append(root_id)
	return root_incident_ids


def train_validate_root_incidents_sets(root_incident_ids, percentage):
	num_root_incident_ids = len(root_incident_ids)
	train_idx = round(num_root_incident_ids * percentage)
	train_root_incident_ids = root_incident_ids[:train_idx]
	validate_root_incident_ids = root_incident_ids[train_idx:]
	random.shuffle(train_root_incident_ids)
	random.shuffle(validate_root_incident_ids)
	return train_root_incident_ids, validate_root_incident_ids


def get_positive_data(cur, root_incident_ids, sent0, sent1, labels):
	for root_incident_id in root_incident_ids:
		cur.execute("SELECT content FROM incidents WHERE id = ?", (root_incident_id, ))
		prompt, = cur.fetchone()
		cur.execute("""
		SELECT
			incidents.content
		FROM classifications
		JOIN incidents ON incidents.id = classifications.child_incident_id
		WHERE classifications.root_incident_id = ? AND classifications.soft_hard_pos_neg = 0
		""", (root_incident_id, ))
		soft_positives = cur.fetchall()
		for soft_pos, in soft_positives:
			sent0.append(prompt)
			sent1.append(soft_pos)
			labels.append(0)
	return (sent0, sent1, labels)


def get_negative_data(cur, root_incident_ids, sent0, sent1, labels):
	for root_incident_id in root_incident_ids:
		cur.execute("SELECT content FROM incidents WHERE id = ?", (root_incident_id, ))
		prompt, = cur.fetchone()
		cur.execute("""
		SELECT
			incidents.content
		FROM classifications
		JOIN incidents ON incidents.id = classifications.child_incident_id
		WHERE classifications.root_incident_id = ? AND classifications.soft_hard_pos_neg IN (2, 3)
		""", (root_incident_id, ))
		soft_hard_negatives = cur.fetchall()
		for negative, in soft_hard_negatives:
			sent0.append(prompt)
			sent1.append(negative)
			labels.append(1)
	return (sent0, sent1, labels)


def get_data(cur, root_incident_ids):
	sent0, sent1, labels = get_positive_data(cur, root_incident_ids, [], [], [])
	sent0, sent1, labels = get_negative_data(cur, root_incident_ids, sent0, sent1, labels)
	return sent0, sent1, labels


def get_dataloader(sent0, sent1, labels, tokenizer, batch_size):
	inputs = tokenizer(sent0, sent1, return_tensors="pt", max_length=512, truncation=True, padding="max_length")
	inputs["labels"] = torch.LongTensor([labels]).T
	dataset = IncidentDataset(inputs)
	dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
	return dataloader


def train_loop(dataloader, device, model, optimizer, loss_fn, model_name, epoch):
	len_dataloader = len(dataloader)
	total_loss = 0
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
		loss_item = loss.item()
		total_loss += loss_item
		print(f"loss: {loss_item:>7f}")
	avg_loss = total_loss / len_dataloader
	save_checkpoint(epoch+1, model, optimizer, avg_loss, f"{model_name}-epoch{epoch+1}.pth")


def validate_loop(dataloader, device, model, loss_fn, model_name, epoch):
	total_dataset = len(dataloader.dataset)
	len_dataloader = len(dataloader)
	total_loss = 0
	correct = 0
	with torch.no_grad():
		for batch in dataloader:
			input_ids = batch["input_ids"].to(device)
			token_type_ids = batch["token_type_ids"].to(device)
			attention_mask = batch["attention_mask"].to(device)
			labels = batch["labels"].to(device)
			output = model(input_ids, token_type_ids=token_type_ids, attention_mask=attention_mask, labels=labels)
			correct += (output.logits.argmax(1) == labels.squeeze()).type(torch.float).sum().item()
			loss = loss_fn(output.logits, labels.squeeze_())
			loss_item = loss.item()
			total_loss += loss_item
			print(f"loss: {loss_item:>7f}")
	avg_loss = total_loss / len_dataloader
	accuracy = correct / total_dataset
	with open(f"validation-{model_name}.txt", "a") as f:
		f.write(f"{model_name}-epoch{epoch+1}.pth, Avg loss: {avg_loss}, Accuracy: {accuracy}\n")


def save_checkpoint(epoch, model, optimizer, avg_loss, checkpoint_path):
	checkpoint = {
		"epoch": epoch,
		"model_state_dict": model.state_dict(),
		"optimizer_state_dict": optimizer.state_dict(),
		"avg_loss": avg_loss
	}
	torch.save(checkpoint, checkpoint_path)


def load_checkpoint(checkpoint_path):
	checkpoint = torch.load(checkpoint_path)
	epoch = checkpoint["epoch"]
	model_state_dict = checkpoint["model_state_dict"]
	optimizer_state_dict = checkpoint["optimizer_state_dict"]
	avg_loss = checkpoint["avg_loss"]
	return epoch, model_state_dict, optimizer_state_dict, avg_loss


def main():
	transformers.logging.set_verbosity_error()
	device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
	learning_rate = 1e-3
	epochs = 4
	batch_size = 16
	tokenizer = transformers.AutoTokenizer.from_pretrained("bert-base-uncased")
	model = transformers.BertForNextSentencePrediction.from_pretrained("bert-base-uncased").to(device)
	optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
	loss_fn = torch.nn.CrossEntropyLoss()
	model_name = "model2"

	with database.connect(database="classification-model2.sqlite") as con:
		cur = con.cursor()
		root_incident_ids = get_all_root_incidents(cur)
		train_root_incident_ids, validate_root_incident_ids = train_validate_root_incidents_sets(root_incident_ids, 0.9)

		sent0_train, sent1_train, labels_train = get_data(cur, train_root_incident_ids)
		sent0_validate, sent1_validate, labels_validate = get_data(cur, validate_root_incident_ids)
		train_dataloader = get_dataloader(sent0_train, sent1_train, labels_train, tokenizer, batch_size)
		validate_dataloader = get_dataloader(sent0_validate, sent1_validate, labels_validate, tokenizer, batch_size)

		for epoch in range(epochs):
			print(f"Epoch {epoch + 1}")
			train_loop(train_dataloader, device, model, optimizer, loss_fn, model_name, epoch)
			validate_loop(validate_dataloader, device, model, loss_fn, model_name, epoch)


if __name__ == "__main__":
	main()
