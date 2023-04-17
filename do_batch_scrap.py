from scrap_data import scrap
import threading


def main():
	threads = []
	leftend = 0
	rightend = 10

	for i in range(200):
		t = threading.Thread(target=scrap, args=(f"temp{i}.sqlite", leftend, rightend))
		leftend = rightend + 1
		rightend = rightend + 10
		threads.append(t)
		t.start()

	for thread in threads:
		thread.join()


if __name__ == "__main__":
	main()
