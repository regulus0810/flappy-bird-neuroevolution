import pygame
import random
import os

import config
import entities
from model_brain import linear_brain


# 1. Khởi tạo Pygame và Cửa sổ Game
pygame.init()
WIDTH, HEIGHT = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
FPS = config.FPS

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Solo với AI (Chơi cùng AI)")
clock = pygame.time.Clock()
running = True
pausing = False

# 2. Phông chữ hiển thị
font = pygame.font.SysFont("sans", 24, bold=True)
small_font = pygame.font.SysFont("sans", 16, bold=True)
big_font = pygame.font.SysFont("sans", 36, bold=True)

# 3. Tải hình ảnh (kèm fallback dự phòng)
ASSETS_DIR = "assets"

def load_image(filename, size=None):
	path = os.path.join(ASSETS_DIR, filename)
	if os.path.exists(path):
		try:
			img = pygame.image.load(path)
			img = img.convert_alpha() if filename.endswith(".png") else img.convert()
			if size:
				img = pygame.transform.scale(img, size)
			return img
		except pygame.error:
			return None
	return None

bg_img = load_image("background-day.png", (WIDTH, HEIGHT))
player_img = load_image("yellowbird-midflap.png", (config.BIRD_WIDTH, config.BIRD_HEIGHT))
ai_img = load_image("bluebird-midflap.png", (config.BIRD_WIDTH, config.BIRD_HEIGHT))
pipe_raw = load_image("pipe-green.png")
gameover_img = load_image("gameover.png")

if pipe_raw:
	pipe_down_img = pygame.transform.scale(pipe_raw, (config.TUBE_WIDTH, HEIGHT))
	pipe_top_img = pygame.transform.flip(pipe_down_img, False, True)
else:
	pipe_down_img = None
	pipe_top_img = None

# 4. Hàm khởi tạo / Reset ván đấu
def reset_game():
	player = entities.LinearBird(config.BIRD_START_Y)
	ai = entities.LinearBird(config.BIRD_START_Y)

	# Nạp bộ gene tốt nhất cho AI từ file best_bird.json
	ai.chromosome = linear_brain.load_best_bird("best_bird.json")

	# Khởi tạo 4 cột để phủ kín chiều rộng màn hình 700px
	tubes_list = [entities.Tube(WIDTH + i * config.TUBE_INTERVAL) for i in range(4)]
	return player, ai, tubes_list

bird_player, bird_ai, tubes = reset_game()

# 5. Vòng lặp trò chơi
while running:
	clock.tick(FPS)

	# --- A. Vẽ hình nền ---
	if bg_img:
		screen.blit(bg_img, (0, 0))
	else:
		screen.fill(config.BACKGROUND_COLOR)

	# --- B. Tìm cột gần nhất phía trước chim ---
	ahead_tubes = [t for t in tubes if t.x + t.width >= config.BIRD_X]
	nearest_tube = min(ahead_tubes, key=lambda t: t.x) if ahead_tubes else None

	# --- C. Cập nhật AI ---
	if bird_ai.alive and not pausing:
		if nearest_tube:
			inputs = entities.get_inputs(bird_ai, nearest_tube)
			bird_ai.think_and_act(inputs)
		bird_ai.fly_down()
		if bird_ai.y <= 0 or bird_ai.y + bird_ai.height >= HEIGHT:
			bird_ai.alive = False

	# --- D. Cập nhật Người chơi ---
	if bird_player.alive and not pausing:
		bird_player.fly_down()
		if bird_player.y <= 0 or bird_player.y + bird_player.height >= HEIGHT:
			bird_player.alive = False

	# --- E. Vẽ tia nhìn của AI (laser vision) ---
	if bird_ai.alive and nearest_tube:
		ai_center = (bird_ai.x + bird_ai.width // 2, bird_ai.y + bird_ai.height // 2)
		pygame.draw.line(screen, config.NEON_PINK, ai_center, (nearest_tube.x, nearest_tube.height), width=2)
		pygame.draw.line(screen, config.NEON_CYAN, ai_center, (nearest_tube.x, nearest_tube.height + nearest_tube.gate_height), width=2)

	# --- F. Cập nhật và vẽ các cột ---
	for tube in tubes:
		top_rect = pygame.Rect(tube.x, 0, tube.width, tube.height)
		down_rect = pygame.Rect(tube.x, tube.height + tube.gate_height, tube.width, HEIGHT - tube.height - tube.gate_height)

		# Vẽ ống
		if pipe_top_img and pipe_down_img:
			screen.blit(pipe_top_img, (tube.x, tube.height - HEIGHT))
			screen.blit(pipe_down_img, (tube.x, tube.height + tube.gate_height))
		else:
			pygame.draw.rect(screen, config.TUBE_COLOR, top_rect)
			pygame.draw.rect(screen, config.TUBE_COLOR, down_rect)

		# Di chuyển cột sang trái
		if not pausing:
			tube.x -= tube.velocity

		# Kiểm tra va chạm với cột
		for b in [bird_player, bird_ai]:
			if b.alive:
				rect = b.get_rect()
				if rect.colliderect(top_rect) or rect.colliderect(down_rect):
					b.alive = False

		# Cập nhật điểm khi vượt qua cột
		if tube.x + tube.width <= config.BIRD_X and not tube.passed:
			if bird_player.alive:
				bird_player.score += 1
			if bird_ai.alive:
				bird_ai.score += 1
			tube.passed = True

		# Tái tạo cột mới khi đi hết màn hình bên trái
		if tube.x <= -tube.width:
			max_x = max(t.x for t in tubes)
			tube.x = max_x + config.TUBE_INTERVAL
			tube.height = random.randint(int(HEIGHT * 0.3), int(HEIGHT * 0.6))
			tube.passed = False

	# --- G. Vẽ chim và nhãn tên ---
	# Chim AI
	if bird_ai.alive:
		if ai_img:
			screen.blit(ai_img, (bird_ai.x, bird_ai.y))
		else:
			pygame.draw.rect(screen, config.NEON_PINK, (bird_ai.x, bird_ai.y, bird_ai.width, bird_ai.height))
		tag_ai = small_font.render("AI", True, config.NEON_PINK)
		screen.blit(tag_ai, (bird_ai.x + bird_ai.width // 2 - tag_ai.get_width() // 2, bird_ai.y - 18))

	# Chim Người chơi
	if bird_player.alive:
		if player_img:
			screen.blit(player_img, (bird_player.x, bird_player.y))
		else:
			pygame.draw.rect(screen, config.NEON_CYAN, (bird_player.x, bird_player.y, bird_player.width, bird_player.height))
		tag_you = small_font.render("YOU", True, config.NEON_CYAN)
		screen.blit(tag_you, (bird_player.x + bird_player.width // 2 - tag_you.get_width() // 2, bird_player.y - 18))

	# --- H. Bảng điểm song song ---
	player_score_txt = font.render(f"YOU: {bird_player.score}", True, config.NEON_CYAN)
	ai_score_txt = font.render(f"AI: {bird_ai.score}", True, config.NEON_PINK)
	screen.blit(player_score_txt, (20, 20))
	screen.blit(ai_score_txt, (WIDTH - ai_score_txt.get_width() - 20, 20))

	# --- I. Trạng thái Game Over & Phân định thắng thua ---
	if not bird_player.alive and not bird_ai.alive:
		pausing = True

	if pausing:
		if gameover_img:
			screen.blit(gameover_img, (WIDTH // 2 - gameover_img.get_width() // 2, HEIGHT // 2 - 120))

		# Xác định kết quả
		if bird_player.score > bird_ai.score:
			result_txt = big_font.render("YOU WIN!", True, config.NEON_CYAN)
		elif bird_player.score < bird_ai.score:
			result_txt = big_font.render("AI WINS!", True, config.NEON_PINK)
		else:
			result_txt = big_font.render("DRAW (HÒA)!", True, config.TEXT_COLOR)

		screen.blit(result_txt, (WIDTH // 2 - result_txt.get_width() // 2, HEIGHT // 2 - 20))
		press_space_txt = font.render("Press SPACE to play again", True, config.TEXT_COLOR)
		screen.blit(press_space_txt, (WIDTH // 2 - press_space_txt.get_width() // 2, HEIGHT // 2 + 40))

	# --- J. Bắt sự kiện bàn phím ---
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				if pausing:
					bird_player, bird_ai, tubes = reset_game()
					pausing = False
				else:
					if bird_player.alive:
						bird_player.fly_up()

	pygame.display.flip()

pygame.quit()
