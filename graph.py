import matplotlib.pyplot as plt



with open("okay.txt") as f:
	lines = f.readlines()
	x = []
	y = []
	for idx, line in enumerate(lines):
		line = float(line.replace("loss: ", ""))
		x.append(idx)
		y.append(line)
	plt.ylim(0, 1)
	plt.plot(x, y)
	plt.show()