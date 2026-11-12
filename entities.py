import pygame
import random
import config
from model_brain import linear_brain
from model_brain import mlp_brain

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
		self.fitness = 0
		self.alive = True
		self.time_alive = 0
		self.score = 0

	def fly_up(self):
		self.velocity = 0
		self.velocity -= self.flap

	def fly_down(self):
		self.y += self.velocity
		self.velocity += self.gravity

	def get_rect(self):
		return pygame.Rect(self.x, self.y, self.width, self.height)

# Linear Brain
class LinearBird(Bird):
	def __init__(self, y):
		super().__init__(y)
		# Gene of linear bird: 6 (5 weights + 1 bias)
		self.chromosome = [random.uniform(-3.0, 3.0) for _ in range(config.NUM_PARAMETERS)]

		self.brain = linear_brain.LinearBrain(self.chromosome)

	def think_and_act(self, inputs):
		output = self.brain.predict(inputs)
		if output > 0.45 and self.velocity > 0:
			self.fly_up()

# Mlp Brain
class MlpBird(Bird):
    def __init__(self, y):
        super().__init__(y)
        # 1. Cấp đúng 89 số gen ngẫu nhiên
        self.chromosome = [random.uniform(-1.0, 1.0) for _ in range(config.MlpConfig.NUM_PARAMETERS)]
        
        # 2. Gắn bộ não MLP vào chim
        self.brain = mlp_brain.MlpBrain()
        self.brain.set_weights(self.chromosome)

    def think_and_act(self, inputs):
        # 3. Cho não MLP suy nghĩ và ra quyết định
        output = self.brain.predict(inputs)
        if output > 0.45 and self.velocity > 0:
            self.fly_up()

class Tube:
	def __init__(self, x):
		self.x = x
		self.y = 0
		self.width = config.TUBE_WIDTH
		self.height = random.randint(int(config.SCREEN_HEIGHT  * 0.3), int(config.SCREEN_HEIGHT  * 0.6))
		self.velocity = config.TUBE_VELOCITY
		self.gate_height = config.GATE_HEIGHT
		self.tube_interval = config.TUBE_INTERVAL
		self.passed = False


	# def get_rect(self):
	# 	top_rect = pygame.Rect(self.x, self.y - config.TUBE_HEIGHT, config.TUBE_WIDTH, config.TUBE_HEIGHT)
	# 	down_rect = pygame.Rect(self.x, self.y + config.GATE_HEIGHT, config.TUBE_WIDTH, config.TUBE_HEIGHT)
	# 	return top_rect, down_rect

# Get feature information of bird
def get_inputs(bird, tube):
	# index of bird
	bird_y_center = bird.y + bird.height // 2
	# bird velocity
	bird_velo = bird.velocity
	# distance bird to nearest tube
	dis_nearest_tube = tube.x - (bird.x + bird.width)
	# distance to top and bottum tube
	dis_top_tube = bird.y - tube.height
	dis_buttom_tube = (tube.height + tube.gate_height) - (bird.y + bird.height)

	return [
		bird_y_center / config.SCREEN_HEIGHT,
		bird_velo / 10.0,
		dis_nearest_tube / config.SCREEN_WIDTH,
		dis_top_tube / config.SCREEN_HEIGHT,
		dis_buttom_tube / config.SCREEN_HEIGHT
	]

if __name__ == "__main__":
	# 1. Bộ gene kiểm thử
	BEST_CHROMOSOME = [
		-0.15276927852520564,
		0.10256978306696486,
		0.06003522901299302,
		0.9097261008986717,
		-2.839533671862189,
		0.026371543632180305,
	]

	# 2. Danh sách các test cases
	test_cases = [
		{
			"name": "Case 1: Bias cao + chim đang rơi -> Phải nhảy",
			"chromosome": [0, 0, 0, 0, 0, 2.0],
			"inputs": [0.5, 0.3, 0.4, 0.1, 0.1],
			"initial_velocity": 4.0,
			"expected_act": True,
		},
		{
			"name": "Case 2: Bias thấp + chim đang rơi -> Không nhảy",
			"chromosome": [0, 0, 0, 0, 0, -2.0],
			"inputs": [0.5, 0.3, 0.4, 0.1, 0.1],
			"initial_velocity": 4.0,
			"expected_act": False,
		},
		{
			"name": "Case 3: Output cao nhưng chim đang bay lên (vel <= 0) -> Không nhảy",
			"chromosome": [0, 0, 0, 0, 0, 2.0],
			"inputs": [0.5, -0.4, 0.4, 0.1, 0.1],
			"initial_velocity": -5.0,
			"expected_act": False,
		},
		{
			"name": "Case 4: Game thực tế - Rơi thấp dưới khe hở (best_bird.json)",
			"chromosome": BEST_CHROMOSOME,
			"inputs": [0.68, 0.60, 0.25, 0.28, -0.12],
			"initial_velocity": 6.0,
			"expected_act": True,
		},
		{
			"name": "Case 5: Game thực tế - Đang ở vị trí cao (best_bird.json)",
			"chromosome": BEST_CHROMOSOME,
			"inputs": [0.20, -0.50, 0.35, -0.20, 0.38],
			"initial_velocity": -5.0,
			"expected_act": False,
		},
	]

	print("=== KIỂM THỬ HÀM think_and_act() ===")
	for tc in test_cases:
		# Khởi tạo chim giả lập không cần surface pygame
		bird = LinearBird(y=300)
		bird.chromosome = tc["chromosome"]
		bird.velocity = tc["initial_velocity"]

		# Tính toán trước output của mạng để đối chiếu
		nb = linear_brain.LinearBrain(bird.chromosome)
		predicted_output = nb.predict(tc["inputs"])

		# Thực thi hàm
		bird.think_and_act(tc["inputs"])
		acted = bird.velocity == -bird.flap

		passed = acted == tc["expected_act"]
		status = "PASS" if passed else "FAIL"

		print(f"\n[{status}] {tc['name']}")
		print(f"  - Output nơ-ron: {predicted_output:.4f} (Ngưỡng: > 0.45)")
		print(f"  - Vận tốc ban đầu: {tc['initial_velocity']} -> Vận tốc sau xử lý: {bird.velocity}")
		print(f"  - Hành động: {'NHẢY (fly_up)' if acted else 'KHÔNG NHẢY'}")
