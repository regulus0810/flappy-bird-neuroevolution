import os
import random
import pygame

import config
import entities

# ==============================================================================
# 1. Initialize Pygame and Game Window
# ==============================================================================
pygame.init()
WIDTH, HEIGHT = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
FPS = config.FPS

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Battle Arena (Human & AI)")
clock = pygame.time.Clock()

# Fonts for rendering UI and HUD
font = pygame.font.SysFont("sans", 24, bold=True)
small_font = pygame.font.SysFont("sans", 16, bold=True)
big_font = pygame.font.SysFont("sans", 36, bold=True)

# ==============================================================================
# 2. Asset Loader with Fallback
# ==============================================================================
def load_image(filename, size=None):
    """Load an image from assets directory with fallback handling."""
    path = os.path.join(config.ASSETS_DIR, filename)
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
user_img = load_image("yellowbird-midflap.png", (config.BIRD_WIDTH, config.BIRD_HEIGHT))
linear_img = load_image("bluebird-midflap.png", (config.BIRD_WIDTH, config.BIRD_HEIGHT))
mlp_img = load_image("redbird-midflap.png", (config.BIRD_WIDTH, config.BIRD_HEIGHT))
pipe_raw = load_image("pipe-green.png")
gameover_img = load_image("gameover.png")

# Prepare pipes
if pipe_raw:
    pipe_down_img = pygame.transform.scale(pipe_raw, (config.TUBE_WIDTH, HEIGHT))
    pipe_top_img = pygame.transform.flip(pipe_down_img, False, True)
else:
    pipe_down_img = None
    pipe_top_img = None

# ==============================================================================
# 3. Game Mode Configurations
# 1: AI vs AI (Linear vs MLP)
# 2: User vs Linear AI
# 3: User vs MLP AI
# ==============================================================================
current_mode = 1    # Default mode: AI vs AI
fast_mode = False   # Fast speed toggle for AI vs AI mode

def create_bird(bird_type):
    """Factory function to instantiate and load weights for birds."""
    if bird_type == "user":
        bird = entities.Bird(config.BIRD_START_Y)
        info = {"name": "YOU", "img": user_img, "color": config.TEXT_COLOR, "is_ai": False}
        return bird, info

    elif bird_type == "linear":
        bird = entities.LinearBird(config.BIRD_START_Y)
        bird.load_best_bird(config.LinearConfig.CHECKPOINT_FILE)
        info = {"name": "LINEAR AI", "img": linear_img, "color": config.NEON_CYAN, "is_ai": True}
        return bird, info

    elif bird_type == "mlp":
        bird = entities.MlpBird(config.BIRD_START_Y)
        bird.load_best_bird(config.MlpConfig.CHECKPOINT_FILE)
        info = {"name": "MLP AI", "img": mlp_img, "color": config.NEON_PINK, "is_ai": True}
        return bird, info

def reset_game(mode):
    """Reset match entities based on selected game mode."""
    if mode == 1:
        # Mode 1: AI vs AI (Linear vs MLP)
        bird1, info1 = create_bird("linear")
        bird2, info2 = create_bird("mlp")
    elif mode == 2:
        # Mode 2: User vs Linear AI
        bird1, info1 = create_bird("user")
        bird2, info2 = create_bird("linear")
    else:
        # Mode 3: User vs MLP AI
        bird1, info1 = create_bird("user")
        bird2, info2 = create_bird("mlp")

    # Initialize 4 obstacles across the screen
    tubes_list = [entities.Tube(WIDTH + i * config.TUBE_INTERVAL) for i in range(4)]
    return bird1, info1, bird2, info2, tubes_list

# Initialize starting match
bird1, info1, bird2, info2, tubes = reset_game(current_mode)
running = True
pausing = False

# ==============================================================================
# 4. Main Gameplay Loop
# ==============================================================================
while running:
    # Clock speed management: Max speed only if enabled in AI vs AI mode
    if current_mode == 1 and fast_mode:
        clock.tick(0)
    else:
        clock.tick(FPS)

    # --- A. Render Background ---
    if bg_img:
        screen.blit(bg_img, (0, 0))
    else:
        screen.fill(config.BACKGROUND_COLOR)

    # --- B. Locate Nearest Ahead Tube ---
    ahead_tubes = [t for t in tubes if t.x + t.width >= config.BIRD_X]
    nearest_tube = min(ahead_tubes, key=lambda t: t.x) if ahead_tubes else None

    # --- C. Update Bird Physics and AI Actions ---
    for bird, info in [(bird1, info1), (bird2, info2)]:
        if bird.alive and not pausing:
            # AI decision making and raycast laser vision
            if info["is_ai"] and nearest_tube:
                inputs = entities.get_inputs(bird, nearest_tube)
                bird.think_and_act(inputs)

            # Apply gravity
            bird.fly_down()

            # Boundary collision check (ceiling and floor)
            if bird.y <= 0 or bird.y + bird.height >= HEIGHT:
                bird.alive = False

    # --- D. Draw Laser Rays for AI Birds ---
    if nearest_tube:
        for bird, info in [(bird1, info1), (bird2, info2)]:
            if bird.alive and info["is_ai"]:
                bird_center = (bird.x + bird.width // 2, bird.y + bird.height // 2)
                pygame.draw.line(screen, info["color"], bird_center, (nearest_tube.x, nearest_tube.height), width=2)
                pygame.draw.line(screen, info["color"], bird_center, (nearest_tube.x, nearest_tube.height + nearest_tube.gate_height), width=2)

    # --- E. Move and Render Pipes ---
    for tube in tubes:
        top_rect = pygame.Rect(tube.x, 0, tube.width, tube.height)
        down_rect = pygame.Rect(tube.x, tube.height + tube.gate_height, tube.width, HEIGHT - tube.height - tube.gate_height)

        # Draw pipes
        if pipe_top_img and pipe_down_img:
            screen.blit(pipe_top_img, (tube.x, tube.height - HEIGHT))
            screen.blit(pipe_down_img, (tube.x, tube.height + tube.gate_height))
        else:
            pygame.draw.rect(screen, config.TUBE_COLOR, top_rect)
            pygame.draw.rect(screen, config.TUBE_COLOR, down_rect)

        # Move tube leftwards
        if not pausing:
            tube.x -= tube.velocity

        # Pipe collision detection
        for b in [bird1, bird2]:
            if b.alive:
                rect = b.get_rect()
                if rect.colliderect(top_rect) or rect.colliderect(down_rect):
                    b.alive = False

        # Scoring update when clearing pipe
        if tube.x + tube.width <= config.BIRD_X and not tube.passed:
            if bird1.alive:
                bird1.score += 1
            if bird2.alive:
                bird2.score += 1
            tube.passed = True

        # Recycle pipes when off-screen
        if tube.x <= -tube.width:
            max_x = max(t.x for t in tubes)
            tube.x = max_x + config.TUBE_INTERVAL
            tube.height = random.randint(int(HEIGHT * 0.3), int(HEIGHT * 0.6))
            tube.passed = False

    # --- F. Draw Birds and Identification Badges ---
    for bird, info in [(bird1, info1), (bird2, info2)]:
        if bird.alive:
            if info["img"]:
                screen.blit(info["img"], (bird.x, bird.y))
            else:
                pygame.draw.rect(screen, info["color"], (bird.x, bird.y, bird.width, bird.height))

            # Render badge tag above bird
            tag = small_font.render(info["name"], True, info["color"])
            screen.blit(tag, (bird.x + bird.width // 2 - tag.get_width() // 2, bird.y - 18))

    # --- G. Render Scoreboard and Mode Indicator ---
    score1_txt = font.render(f"{info1['name']}: {bird1.score}", True, info1["color"])
    score2_txt = font.render(f"{info2['name']}: {bird2.score}", True, info2["color"])
    screen.blit(score1_txt, (20, 20))
    screen.blit(score2_txt, (WIDTH - score2_txt.get_width() - 20, 20))

    # Controls guide and Fast Mode HUD at bottom
    if current_mode == 1:
        speed_badge = "MAX" if fast_mode else "60 FPS"
        guide_txt = small_font.render(f"[1] AI vs AI  |  [2] vs Linear  |  [3] vs MLP  |  [F] Speed: {speed_badge}", True, config.NEON_CYAN)
    else:
        guide_txt = small_font.render("[1] AI vs AI  |  [2] vs Linear  |  [3] vs MLP  |  [SPACE] Jump / Restart", True, config.TEXT_COLOR)
    screen.blit(guide_txt, (WIDTH // 2 - guide_txt.get_width() // 2, HEIGHT - 30))

    # --- H. Match Over Check and Winner Declaration ---
    if not bird1.alive and not bird2.alive:
        pausing = True

    if pausing:
        if gameover_img:
            screen.blit(gameover_img, (WIDTH // 2 - gameover_img.get_width() // 2, HEIGHT // 2 - 120))

        # Determine winner
        if bird1.score > bird2.score:
            winner_txt = big_font.render(f"{info1['name']} WINS!", True, info1["color"])
        elif bird2.score > bird1.score:
            winner_txt = big_font.render(f"{info2['name']} WINS!", True, info2["color"])
        else:
            winner_txt = big_font.render("DRAW (TIED)!", True, config.TEXT_COLOR)

        screen.blit(winner_txt, (WIDTH // 2 - winner_txt.get_width() // 2, HEIGHT // 2 - 20))
        restart_prompt = font.render("Press SPACE to play again, or [1-3] to switch mode", True, config.TEXT_COLOR)
        screen.blit(restart_prompt, (WIDTH // 2 - restart_prompt.get_width() // 2, HEIGHT // 2 + 35))

    # --- I. Event and Keyboard Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Switch game modes via number keys 1, 2, 3
            if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                current_mode = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3}[event.key]
                # Reset fast mode to False when leaving AI vs AI mode for safety
                if current_mode != 1:
                    fast_mode = False
                bird1, info1, bird2, info2, tubes = reset_game(current_mode)
                pausing = False

            # Toggle fast-forward mode (Available in AI vs AI mode)
            elif event.key == pygame.K_f:
                if current_mode == 1:
                    fast_mode = not fast_mode

            # Spacebar action: flap for player, or restart if paused
            elif event.key == pygame.K_SPACE:
                if pausing:
                    bird1, info1, bird2, info2, tubes = reset_game(current_mode)
                    pausing = False
                else:
                    # Flap player bird if in user mode
                    if not info1["is_ai"] and bird1.alive:
                        bird1.fly_up()

    pygame.display.flip()

pygame.quit()