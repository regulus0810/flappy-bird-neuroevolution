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

# Color definitions
WHITE = (255, 255, 255)
MENU_BOX_BG = (25, 30, 42)
MENU_BOX_HOVER = (45, 55, 75)
MENU_BORDER = (120, 130, 160)
MENU_BORDER_ACTIVE = (255, 255, 255)

# Fonts for rendering UI, buttons, and HUD
font = pygame.font.SysFont("sans", 24, bold=True)
small_font = pygame.font.SysFont("sans", 16, bold=True)
big_font = pygame.font.SysFont("sans", 36, bold=True)
title_font = pygame.font.SysFont("sans", 40, bold=True)

# ==============================================================================
# 2. Asset Loader with Fallback Handling
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

# Prepare pipe surfaces
if pipe_raw:
    pipe_down_img = pygame.transform.scale(pipe_raw, (config.TUBE_WIDTH, HEIGHT))
    pipe_top_img = pygame.transform.flip(pipe_down_img, False, True)
else:
    pipe_down_img = None
    pipe_top_img = None

# ==============================================================================
# 3. Game Mode Configurations & Factory
# ==============================================================================
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

def create_tubes():
    """Create starting pipes matching exact training positions."""
    return [entities.Tube(config.BIRD_X + 240 + i * config.TUBE_INTERVAL) for i in range(4)]

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

    # Pipes match exact training distance
    tubes_list = create_tubes()
    return bird1, info1, bird2, info2, tubes_list

# Menu Card Boxes (X, Y, Width, Height)
MENU_BOXES = [
    {"mode": 1, "rect": pygame.Rect(100, 210, 500, 95), "title": "[ 1 ]  AI vs AI", "desc": "Linear Perceptron vs MLP Neural Network", "icons": (linear_img, mlp_img)},
    {"mode": 2, "rect": pygame.Rect(100, 335, 500, 95), "title": "[ 2 ]  USER vs LINEAR AI", "desc": "Play as Yellow Bird vs Blue Linear AI", "icons": (user_img, linear_img)},
    {"mode": 3, "rect": pygame.Rect(100, 460, 500, 95), "title": "[ 3 ]  USER vs MLP AI", "desc": "Play as Yellow Bird vs Red MLP Neural Network", "icons": (user_img, mlp_img)},
]

# State variables
in_menu = True        # Launch directly into the 3-box selection menu
current_mode = 1
fast_mode = False
running = True
pausing = False

bird1, info1, bird2, info2, tubes = None, None, None, None, None

def start_match(mode):
    """Start game with selected mode."""
    global in_menu, current_mode, fast_mode, pausing, bird1, info1, bird2, info2, tubes
    current_mode = mode
    fast_mode = False
    pausing = False
    in_menu = False
    bird1, info1, bird2, info2, tubes = reset_game(current_mode)

# ==============================================================================
# 4. Main Event & Game Loop
# ==============================================================================
while running:
    # --------------------------------------------------------------------------
    # STATE A: 3-BOX MENU SCREEN
    # --------------------------------------------------------------------------
    if in_menu:
        clock.tick(FPS)

        # Draw Background
        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill(config.BACKGROUND_COLOR)

        # Title & Subtitle in pure White
        title_surf = title_font.render("FLAPPY BIRD ARENA", True, WHITE)
        sub_surf = font.render("CHOOSE GAME MODE", True, WHITE)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 80))
        screen.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, 140))

        mouse_pos = pygame.mouse.get_pos()

        # Render 3 Selection Boxes
        for box in MENU_BOXES:
            rect = box["rect"]
            is_hover = rect.collidepoint(mouse_pos)

            bg_color = MENU_BOX_HOVER if is_hover else MENU_BOX_BG
            border_color = MENU_BORDER_ACTIVE if is_hover else MENU_BORDER
            border_thickness = 3 if is_hover else 2

            pygame.draw.rect(screen, bg_color, rect, border_radius=14)
            pygame.draw.rect(screen, border_color, rect, width=border_thickness, border_radius=14)

            # Titles in WHITE
            box_title = font.render(box["title"], True, WHITE)
            box_desc = small_font.render(box["desc"], True, WHITE)
            screen.blit(box_title, (rect.x + 25, rect.y + 18))
            screen.blit(box_desc, (rect.x + 25, rect.y + 54))

            # Bird sprite previews inside box
            icon1, icon2 = box["icons"]
            if icon1:
                screen.blit(icon1, (rect.x + rect.width - 120, rect.y + 30))
            if icon2:
                screen.blit(icon2, (rect.x + rect.width - 60, rect.y + 30))

        # Bottom Instructions in White
        bottom_hint = small_font.render("Click a box or press [1], [2], [3] to start match", True, WHITE)
        screen.blit(bottom_hint, (WIDTH // 2 - bottom_hint.get_width() // 2, HEIGHT - 50))

        # Menu Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for box in MENU_BOXES:
                    if box["rect"].collidepoint(event.pos):
                        start_match(box["mode"])

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    start_match(1)
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    start_match(2)
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    start_match(3)

        pygame.display.flip()
        continue

    # --------------------------------------------------------------------------
    # STATE B: GAMEPLAY SCREEN (PHYSICS 100% MATCHING TRAIN.PY)
    # --------------------------------------------------------------------------
    # Speed control: Max speed allowed only in AI vs AI mode
    if current_mode == 1 and fast_mode:
        clock.tick(0)
    else:
        clock.tick(FPS)

    # Render Background
    if bg_img:
        screen.blit(bg_img, (0, 0))
    else:
        screen.fill(config.BACKGROUND_COLOR)

    # 1. Update and Render Pipes FIRST (Matches train.py execution order)
    for tube in tubes:
        top_rect = pygame.Rect(tube.x, 0, tube.width, tube.height)
        down_rect = pygame.Rect(tube.x, tube.height + tube.gate_height, tube.width, HEIGHT - tube.height - tube.gate_height)

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

        # Recycle pipes (Exact same modulo stride as train.py)
        if tube.x <= -config.TUBE_WIDTH:
            tube.x += len(tubes) * config.TUBE_INTERVAL
            tube.height = random.randint(int(HEIGHT * 0.3), int(HEIGHT * 0.6))
            tube.passed = False

    # 2. Locate Nearest Ahead Pipe AFTER tubes moved (Matches train.py)
    ahead_tubes = [t for t in tubes if t.x + t.width >= config.BIRD_X]
    nearest_tube = min(ahead_tubes, key=lambda t: t.x) if ahead_tubes else None

    # 3. Update Bird Physics and AI Actions
    for bird, info in [(bird1, info1), (bird2, info2)]:
        if bird.alive:
            if not pausing:
                bird.time_alive += 1

                # AI decision making with synchronized inputs
                if info["is_ai"] and nearest_tube:
                    inputs = entities.get_inputs(bird, nearest_tube)
                    bird.think_and_act(inputs)

                bird.fly_down()

                # Boundary collision check (ceiling and floor)
                if bird.y <= 0 or bird.y + bird.height >= HEIGHT:
                    bird.alive = False

    # 4. Draw Laser Rays for AI Birds
    if nearest_tube:
        for bird, info in [(bird1, info1), (bird2, info2)]:
            if bird.alive and info["is_ai"]:
                bird_center = (bird.x + bird.width // 2, bird.y + bird.height // 2)
                pygame.draw.line(screen, info["color"], bird_center, (nearest_tube.x, nearest_tube.height), width=2)
                pygame.draw.line(screen, info["color"], bird_center, (nearest_tube.x, nearest_tube.height + nearest_tube.gate_height), width=2)

    # 5. Draw Birds and Badges
    for bird, info in [(bird1, info1), (bird2, info2)]:
        if bird.alive:
            if info["img"]:
                screen.blit(info["img"], (bird.x, bird.y))
            else:
                pygame.draw.rect(screen, info["color"], (bird.x, bird.y, bird.width, bird.height))

            tag = small_font.render(info["name"], True, info["color"])
            screen.blit(tag, (bird.x + bird.width // 2 - tag.get_width() // 2, bird.y - 18))

    # 6. Render Scoreboard in pure WHITE
    score1_txt = font.render(f"{info1['name']}: {bird1.score}", True, WHITE)
    score2_txt = font.render(f"{info2['name']}: {bird2.score}", True, WHITE)
    screen.blit(score1_txt, (20, 20))
    screen.blit(score2_txt, (WIDTH - score2_txt.get_width() - 20, 20))

    # Controls guide at bottom in pure WHITE
    if current_mode == 1:
        speed_badge = "MAX" if fast_mode else "60 FPS"
        guide_txt = small_font.render(f"[M] Menu  |  [F] Speed: {speed_badge}  |  [SPACE] Pause/Resume", True, WHITE)
    else:
        guide_txt = small_font.render("[M] Menu  |  [SPACE] Jump / Restart  |  [1-3] Switch Mode", True, WHITE)
    screen.blit(guide_txt, (WIDTH // 2 - guide_txt.get_width() // 2, HEIGHT - 30))

    # 7. Match Over Check and Winner Declaration
    if not bird1.alive and not bird2.alive:
        pausing = True

    if pausing:
        if gameover_img:
            screen.blit(gameover_img, (WIDTH // 2 - gameover_img.get_width() // 2, HEIGHT // 2 - 120))

        if bird1.score > bird2.score:
            winner_txt = big_font.render(f"{info1['name']} WINS!", True, WHITE)
        elif bird2.score > bird1.score:
            winner_txt = big_font.render(f"{info2['name']} WINS!", True, WHITE)
        else:
            winner_txt = big_font.render("DRAW (TIED)!", True, WHITE)

        screen.blit(winner_txt, (WIDTH // 2 - winner_txt.get_width() // 2, HEIGHT // 2 - 20))
        restart_prompt = font.render("Press SPACE to replay, or [M] for Menu", True, WHITE)
        screen.blit(restart_prompt, (WIDTH // 2 - restart_prompt.get_width() // 2, HEIGHT // 2 + 35))

    # 8. Gameplay Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Return to menu screen
            if event.key in (pygame.K_m, pygame.K_ESCAPE):
                in_menu = True
                pausing = False

            # Switch game modes directly via number keys
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                start_match({pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3}[event.key])

            # Toggle fast-forward mode in AI vs AI mode
            elif event.key == pygame.K_f:
                if current_mode == 1:
                    fast_mode = not fast_mode

            # Spacebar action: flap for player, or restart if paused
            elif event.key == pygame.K_SPACE:
                if pausing:
                    bird1, info1, bird2, info2, tubes = reset_game(current_mode)
                    pausing = False
                else:
                    if not info1["is_ai"] and bird1.alive:
                        bird1.fly_up()

    pygame.display.flip()

pygame.quit()