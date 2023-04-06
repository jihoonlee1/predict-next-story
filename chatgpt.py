import openai
import os


api_key = os.environ["CHATGPT_API_KEY"]
openai.api_key = api_key


def ask(question):
	response = openai.ChatCompletion.create(
		model="gpt-3.5-turbo",
		messages=[
			{
				"role": "user",
				"content": question
			}
		]
	)
	answer = response["choices"][0]["message"]["content"]
	return answer


