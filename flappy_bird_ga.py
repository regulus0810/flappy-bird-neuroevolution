import pygame
import random

import config
import entities
import genetic_algorithm
import brain

pygame.init()
WIDTH, HEIGHT = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
FPS = config.FPS
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Bird')
clock = pygame.time.Clock()
running = True
font = pygame.font.SysFont('sans', 20)

# --- Color ---
TEXT_COLOR  = config.TEXT_COLOR
NEON_PINK   = config.NEON_PINK    # line from bird cennter to top tube
NEON_CYAN   = config.NEON_CYAN    # line from bird cennter to bottom tube
BLACK = (0,0,0)
YELLOW = (255,255,0)
BIRD_COLOR = config.BIRD_COLOR
TUBE_COLOR = config.TUBE_COLOR
BACKGROUND_COLOR = config.BACKGROUND_COLOR

# --- Tube ---
TUBE_WIDTH = config.TUBE_WIDTH
TUBE_VELOCITY = config.TUBE_VELOCITY
GATE_HEIGHT = config.GATE_HEIGHT	# distance of 2 tubes (tube and tube_inv)
TUBE_INTERVAL = config.TUBE_INTERVAL	# time next tube appear

tube1_x = WIDTH
tube2_x = tube1_x + TUBE_INTERVAL
tube3_x = tube2_x + TUBE_INTERVAL
tube4_x = tube3_x + TUBE_INTERVAL


# --- Bird ---
BIRD_X = WIDTH // 5
BIRD_START_Y = HEIGHT // 2
BIRD_WIDTH = config.BIRD_WIDTH
BIRD_HEIGHT = config.BIRD_HEIGHT
GRAVITY = config.GRAVITY
FLAP_VELOCITY = config.FLAP_VELOCITY 	# speed up of bird


pausing = False     # paussing when score = 10

# -- Setting of genetic algorithm --- 
POP_SIZE = config.POP_SIZE
NUM_INPUTS = config.NUM_INPUTS     # number input of no ron
MUTATION_RATE = config.MUTATION_RATE
MUTATION_SIGMA = config.MUTATION_SIGMA

# Create a population and tubes
population_bird = [entities.Bird(BIRD_START_Y) for _ in range(POP_SIZE)]

tubes = [
	entities.Tube(tube1_x),
	entities.Tube(tube2_x),
	entities.Tube(tube3_x),
	entities.Tube(tube4_x)
]

# --- Init Genetic Algorithm
ga_model = genetic_algorithm.GeneticAlgorithm()
generation = 1

while running:		
	clock.tick(FPS)
	screen.fill(BACKGROUND_COLOR)


	# --- Update alive bird ---
	alive_birds = [b for b in population_bird if b.alive]

	# --- Draw all survival bird ---
	for bird in alive_birds:
		bird_rect = pygame.draw.rect(screen, BIRD_COLOR, (bird.x, bird.y, bird.width, bird.height))

	# --- Draw tube ---
	for tube in tubes:
		# Draw tube
		tube_rect_top = pygame.draw.rect(screen, TUBE_COLOR, (tube.x, tube.y, tube.width, tube.height))

		# Draw tube inverse
		tube_rect_down = pygame.draw.rect(screen, TUBE_COLOR, (tube.x, tube.y + tube.height + tube.gate_height, tube.width, HEIGHT - tube.height - tube.gate_height))

		# Move tube to the left
		if not pausing:
			tube.x -= tube.velocity

		# 1. Check collision with survival bird
		for bird in alive_birds:
			bird_rect = bird.get_rect()
			for obj in [tube_rect_top, tube_rect_down]:
				if bird_rect.colliderect(obj):
					bird.alive = False

			# 2. Set new tube state pass = True and plus score
			if tube.x + tube.width <= bird.x and not tube.passed:
				# check tube pass all live bird
				for bird in alive_birds:
					if bird.alive:
						bird.score += 1
						if bird.score == 50:
							pausing = True
							brain.save_best_bird(bird.chromosome, "best_bird.json")
				tube.passed = True

		# 3. Generate new tubes
		if tube.x <= -TUBE_WIDTH:
			tube.x += len(tubes) * TUBE_INTERVAL
			tube.height = random.randint(int(HEIGHT * 0.3), int(HEIGHT * 0.6))
			tube.passed = False		# Not plus score

	# update fitness
	for bird in alive_birds:
		# increate survival time
		bird.time_alive += 1

		# Tự tìm cột gần nhất đối với CHÍNH CON CHIM NÀY:
		ahead_tubes = [t for t in tubes if t.x + t.width >= bird.x]
		nearest_tube = min(ahead_tubes, key=lambda t: t.x) if ahead_tubes else None

		# bird thingking and decide flap?
		if nearest_tube:
			# Draw 2 line from bird center to top_tube and bottom_tube
			pygame.draw.line(screen, NEON_PINK, (bird.x + bird.width // 2, bird.y + bird.height // 2), (nearest_tube.x, nearest_tube.height), width=2)
			pygame.draw.line(screen, NEON_CYAN, (bird.x + bird.width  // 2, bird.y + bird.height // 2), (nearest_tube.x, nearest_tube.height + nearest_tube.gate_height), width=2)
			inputs = entities.get_inputs(bird, nearest_tube)
			bird.think_and_act(inputs)

		# bird down
		if not pausing:
			bird.fly_down()

		# Kiểm tra va chạm trần và sàn nhà
		if bird.y <= 0 or bird.y + bird.height >= HEIGHT:
			bird.alive = False




	# --- Hiển thị thông tin ---
	gen_txt = font.render(f"Generation: {generation}", True, TEXT_COLOR)
	alive_txt = font.render(f"Alive: {len(alive_birds)}/{POP_SIZE}", True, TEXT_COLOR)
	best_txt  = font.render(f"Best score: {max(b.score for b in population_bird)}", True, TEXT_COLOR)
	screen.blit(gen_txt,   (10, 10))
	screen.blit(alive_txt, (10, 35))
	screen.blit(best_txt,  (10, 60))


	
	# --- if all survival bird dead -> create new generation
	if len(alive_birds) == 0:
		# Calculate fitness for each bird
		for bird in population_bird:
			bird.fitness = bird.score * 100 + bird.time_alive

		# create new generation
		population_bird = ga_model.nex_generation(population_bird)
		generation += 1

		# Reset tube
		tubes = [
			entities.Tube(tube1_x),
			entities.Tube(tube2_x),
			entities.Tube(tube3_x)
		]

	# -- Event button ---
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			# Quit the program
			running = False

	pygame.display.flip()

pygame.quit()