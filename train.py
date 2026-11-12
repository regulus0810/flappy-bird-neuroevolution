import pygame
import random

import config
import entities
import genetic_algorithm

# ---------- 1. Init pygame window ----------
pygame.init()
WIDTH, HEIGHT = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Huấn luyện AI (Genetic Algorithm)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("sans", 20)
small_font = pygame.font.SysFont("sans", 16)

# ---------- 2. Model train config ----------
# Chọn mô hình muốn train: "linear" hoặc "mlp"
MODEL_TYPE = "mlp"

if MODEL_TYPE == "mlp":
	BirdClass = entities.MlpBird
	POP_SIZE = config.MlpConfig.POP_SIZE
	SAVE_FILE = config.MlpConfig.CHECKPOINT_FILE
else:
	BirdClass = entities.LinearBird
	POP_SIZE = config.LinearConfig.POP_SIZE
	SAVE_FILE = config.LinearConfig.CHECKPOINT_FILE

# ---------- 3. Init population and tube ----------
population_bird = [BirdClass(config.BIRD_START_Y) for _ in range(POP_SIZE)]
ga_model = genetic_algorithm.GeneticAlgorithm()

def create_tubes():
	return [entities.Tube(config.BIRD_X + 240 + i * config.TUBE_INTERVAL) for i in range(4)]
tubes = create_tubes()

# Condition state
running = True
pausing = False
fast_mode = True
generation = 1
max_score = 10000

# ---------- 4. While loop train ----------
while running:		
	# fps
	if fast_mode:
		clock.tick(0)
	else:
		clock.tick(config.FPS)

	screen.fill(config.BACKGROUND_COLOR)

	# --- Update alive bird ---
	alive_birds = [b for b in population_bird if b.alive]

	# --- Draw all survival bird ---
	for bird in alive_birds:
		pygame.draw.rect(screen, config.BIRD_COLOR, (bird.x, bird.y, bird.width, bird.height))

	# --- Draw tube ---
	for tube in tubes:
		# Draw tube
		tube_rect_top = pygame.draw.rect(screen, config.TUBE_COLOR, (tube.x, tube.y, tube.width, tube.height))

		# Draw tube inverse
		tube_rect_down = pygame.draw.rect(screen, config.TUBE_COLOR, (tube.x, tube.y + tube.height + tube.gate_height, tube.width, HEIGHT - tube.height - tube.gate_height))

		# Move tube to the left
		if not pausing:
			tube.x -= tube.velocity

		# 1. Check collision with survival bird
		for bird in alive_birds:
			bird_rect = bird.get_rect()
			if bird_rect.colliderect(tube_rect_top) or bird_rect.colliderect(tube_rect_down):
				bird.alive = False

			# 2. Set new tube state pass = True and plus score
			if tube.x + tube.width <= bird.x and not tube.passed:
				for b in alive_birds:
					if b.alive:
						b.score += 1
						# Check score to paussing program
						if b.score == max_score:
							pausing = True
							b.save_best_bird(SAVE_FILE)
				tube.passed = True

		# 3. Generate new tubes
		if tube.x <= -config.TUBE_WIDTH:
			tube.x += len(tubes) * config.TUBE_INTERVAL
			tube.height = random.randint(int(HEIGHT * 0.3), int(HEIGHT * 0.6))
			tube.passed = False		# Not plus score

	# update fitness
	for bird in alive_birds:
		# increate survival time
		bird.time_alive += 1

		# Find nearest tube
		ahead_tubes = [t for t in tubes if t.x + t.width >= bird.x]
		nearest_tube = min(ahead_tubes, key=lambda t: t.x) if ahead_tubes else None

		# bird thingking and decide flap?
		if nearest_tube:
			# Draw 2 line from bird center to top_tube and bottom_tube
			bird_center = (bird.x + bird.width // 2, bird.y + bird.height // 2)
			pygame.draw.line(screen, config.NEON_PINK, bird_center, (nearest_tube.x, nearest_tube.height), width=2)
			pygame.draw.line(screen, config.NEON_CYAN, bird_center, (nearest_tube.x, nearest_tube.height + nearest_tube.gate_height), width=2)

			# Bird decision
			inputs = entities.get_inputs(bird, nearest_tube)
			bird.think_and_act(inputs)

		# bird down
		if not pausing:
			bird.fly_down()

		# Kiểm tra va chạm trần và sàn nhà
		if bird.y <= 0 or bird.y + bird.height >= HEIGHT:
			bird.alive = False


	# --- Hiển thị thông tin ---
	gen_txt   = font.render(f"Gen: {generation} | Model: {MODEL_TYPE.upper()}", True, config.TEXT_COLOR)
	alive_txt = font.render(f"Alive: {len(alive_birds)}/{POP_SIZE}", True, config.TEXT_COLOR)
	best_txt  = font.render(f"Best Score: {max((b.score for b in population_bird), default=0)}", True, config.TEXT_COLOR)
	speed_txt = small_font.render(f"[F] Tốc độ: {'MAX (Tua nhanh)' if fast_mode else '60 FPS (Quan sát)'}", True, config.NEON_CYAN)
	screen.blit(gen_txt,   (10, 10))
	screen.blit(alive_txt, (10, 35))
	screen.blit(best_txt,  (10, 60))
	screen.blit(speed_txt, (10, 85))

	# --- if all survival bird dead -> create new generation
	if len(alive_birds) == 0:
		# create new generation
		population_bird = ga_model.next_generation(population_bird)
		generation += 1

		# Reset tube
		tubes = create_tubes()	

	# -- Event button ---
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_f:
				fast_mode = not fast_mode   # Nhấn F để đổi tốc độ
			elif event.key == pygame.K_SPACE:
				pausing = not pausing       # Nhấn Space để tạm dừng/tiếp tục

	pygame.display.flip()

pygame.quit()