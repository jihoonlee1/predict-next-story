import database
import chatgpt
import re


def main():
	question = 'Come up with five potential follow up headlines and summaries to "Shell sued by regulators in Alabama"'
	answer = chatgpt.ask(question).split("\n\n")
	for a in answer:
		title, body = title_body(a)
		print(title)
		print(body)
		print("")



main()
