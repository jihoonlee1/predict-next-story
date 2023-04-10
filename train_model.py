import database
import random
import re


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
	iteration = 0
	while iteration < num_positives:
		random_number = random.randint(0, num_incidents_all)
		target_incident_id, target_content = incidents_all[random_number]
		cur.execute("SELECT event_id FROM event_incident WHERE incident_id = ?", (target_incident_id, ))
		event_id, = cur.fetchone()
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
		sentence0.append(target_content)
		sentence1.append(unrelated_content)
		labels.append(1)
		iteration += 1
	return (sentence0, sentence1, labels)


def main():
	sentence0, sentence1, labels = [], [], []
	with database.connect() as con:
		cur = con.cursor()
		cur.execute("SELECT id, content FROM incidents")
		incidents_all = cur.fetchall()
		num_incidents_all = len(incidents_all)
		sentence0, sentence1, labels = positive_data(cur, sentence0, sentence1, labels)
		sentence0, sentence1, labels = negative_data(cur, sentence0, sentence1, labels, incidents_all, num_incidents_all)


if __name__ == "__main__":
	main()
