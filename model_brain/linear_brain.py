import numpy as np
import json  # <-- Thêm dòng này vào đầu file

class LinearBrain:
	def __init__(self, chromosome):
		self.weights = np.array(chromosome[:-1], dtype=float)
		self.bias = float(chromosome[-1])

	def predict(self, inputs):
		'''
		inputs[0] = bird.y              # vị trí chim (đang cao hay thấp?)
		inputs[1] = bird.velocity  		# đang rơi nhanh hay chậm?
		inputs[2] = dist_to_tube        # cách cột bao xa?
		inputs[3] = gap_top_y           # khe hở phía trên ở đâu?
		inputs[4] = gap_bottom_y        # khe hở phía dưới ở đâu?

		neuron: y = w * x + b
		-> y = w1 * x1 + w2 * x2 + w3 * x3 + w4 * x4 + w5 * x5 + b
		'''
		x = np.array(inputs, dtype=float)
		y = np.dot(self.weights, x) + self.bias

		# use sigmoid function to decide (output: 0.0 to 1.0)
		output = 1 / (1 + np.exp(-y))

		return output

def save_best_bird(chromosome, filename="best_bird.json"):
	# save best gene to txt
	with open(filename, "w") as f:
		json.dump(chromosome, f, indent=4)
	print(f"Save model successfully to {filename}")

def load_best_bird(filename="best_bird.json"):
	# Read chromosome from best_bird.txt
	with open(filename, "r") as f:
		chromosome = json.load(f)
	return chromosome


if __name__ == "__main__":
	WIDTH, HEIGHT, TUBE_GAP = 480, 640, 150
	chromos = [-1.0, 2.0, 0.0, -3.0, 6.0, -1.0]
	brain = LinearBrain(chromos)

	cases = {
		"A: thấp hơn khe, đang rơi":     dict(bird_y=450, vel=6,  dist=150, top=200),
		"B: cao hơn khe, đang bay lên":  dict(bird_y=80,  vel=-8, dist=150, top=250),
		"C: ngang giữa khe, đứng yên":   dict(bird_y=275, vel=0,  dist=200, top=200),
		"D: sát đất, rơi nhanh":         dict(bird_y=520, vel=9,  dist=60,  top=300),
	}
	for name, c in cases.items():
		inp = [c["bird_y"] / HEIGHT,
			c["vel"] / 10,
			c["dist"] / WIDTH,
			c["top"] / HEIGHT,
			(c["top"] + TUBE_GAP) / HEIGHT]
		out = brain.predict(inp)
		print(f"{name:32s} {np.round(inp, 3).tolist()} -> {out:.3f}", "NHẢY" if out > 0.5 else "không")