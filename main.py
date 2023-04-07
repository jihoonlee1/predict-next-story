import database
import chatgpt
import re


def clean(content):
	content = re.sub(r"[0-9](\.|\)+)", "", content)
	content = re.sub(r"\n+", " ", content).strip()
	return content
