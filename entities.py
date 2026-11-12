import os
import json
import random
import pygame

import config
from model_brain import linear_brain, mlp_brain

class Bird:
	def __init__(self, y):
		self.x = config.BIRD_X
		self.y = y
		self.width = config.BIRD_WIDTH
		self.height = config.BIRD_HEIGHT
		self.velocity = 0
		self.gravity = config.GRAVITY
		self.flap = config.FLAP_VELOCITY

		# --- GA attributes ---
		self.alive = True
		self.time_alive = 0
		self.score = 0
		self.chromosome = []
		self.brain = None

	@property
	def fitness(self):
		# Auto calculate fitness when it was called
		return self.score * 100 + self.time_alive

	def fly_up(self):
		self.velocity = 0
		self.velocity -= self.flap

	def fly_down(self):
		self.y += self.velocity
		self.velocity += self.gravity

	def get_rect(self):
		return pygame.Rect(self.x, self.y, self.width, self.height)

	# Bird think and decided flap or not?
	def think_and_act(self, inputs):
		output = self.brain.predict(inputs)
		if output > 0.45 and self.velocity > 0:
			self.fly_up()

	# Save best chromosome of bird to JSON file
	def save_best_bird(self, filepath):
		chrom = self.chromosome.tolist() if hasattr(self.chromosome, "tolist") else self.chromosome
		os.makedirs(os.path.dirname(filepath), exist_ok=True)
		with open(filepath, "w") as f:
			json.dump(chrom, f, indent=4)
		print(f"-> Đã lưu trọng số vào: {filepath}")

	# Load best chromosome of bird from JSON file
	def load_best_bird(self, filepath):
		if not os.path.exists(filepath):
			raise FileNotFoundError(f"Không tìm thấy file checkpoint: {filepath}")
		with open(filepath, "r") as f:
			self.chromosome = json.load(f)
		# Cập nhật ngay vào não bộ
		if hasattr(self.brain, "set_weights"):
			self.brain.set_weights(self.chromosome)
		else:
			self.brain = linear_brain.LinearBrain(self.chromosome)
		print(f"-> Đã nạp trọng số từ: {filepath}")


# Linear Brain
class LinearBird(Bird):
	def __init__(self, y, chromosome=None):
		super().__init__(y)
		# Gene of linear bird: 6 (5 weights + 1 bias)
		if chromosome is not None:
			self.chromosome = list(chromosome)
		else:
			self.chromosome = [random.uniform(-2.0, 2.0) for _ in range(config.LinearConfig.NUM_PARAMETERS)]
		self.brain = linear_brain.LinearBrain(self.chromosome)

# Mlp Brain
class MlpBird(Bird):
	def __init__(self, y, chromosome=None):
		super().__init__(y)
		# 1. Cấp đúng 89 số gen ngẫu nhiên
		if chromosome is not None:
			self.chromosome = list(chromosome)
		else:
			self.chromosome = [random.uniform(-1.0, 1.0) for _ in range(config.MlpConfig.NUM_PARAMETERS)]
		# 2. Gắn bộ não MLP vào chim
		self.brain = mlp_brain.MlpBrain()
		self.brain.set_weights(self.chromosome)

class Tube:
	def __init__(self, x):
		self.x = x
		self.y = 0
		self.width = config.TUBE_WIDTH
		self.height = random.randint(int(config.SCREEN_HEIGHT * 0.3), int(config.SCREEN_HEIGHT * 0.6))
		self.velocity = config.TUBE_VELOCITY
		self.gate_height = config.GATE_HEIGHT
		self.tube_interval = config.TUBE_INTERVAL
		self.passed = False

# Get feature information of bird
def get_inputs(bird, tube):
	bird_y_center = bird.y + bird.height // 2	# index of bird
	bird_velo = bird.velocity	# bird velocity	
	dis_nearest_tube = tube.x - (bird.x + bird.width)	# distance bird to nearest tube
	dis_top_tube = bird.y - tube.height		# distance to top tube
	dis_bottom_tube = (tube.height + tube.gate_height) - (bird.y + bird.height)		# distance to bottum tube

	return [
		bird_y_center / config.SCREEN_HEIGHT,
		bird_velo / 10.0,
		dis_nearest_tube / config.SCREEN_WIDTH,
		dis_top_tube / config.SCREEN_HEIGHT,
		dis_bottom_tube / config.SCREEN_HEIGHT
	]
