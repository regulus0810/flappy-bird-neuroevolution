import os

# ---------- 1. SCREEN CONFIG ----------
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700
FPS = 120

# --- Color ---
TEXT_COLOR = (235, 240, 255)
NEON_PINK = (255, 60, 170)    # chữ Game over
NEON_CYAN = (60, 230, 255)    # chữ hướng dẫn
BIRD_COLOR = (0, 255, 0)
TUBE_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (0, 0, 0)

# ---------- 2. PHYSICS & ENTITIES ----------
# --- BIRD ---
BIRD_X = SCREEN_WIDTH // 5
BIRD_START_Y = SCREEN_HEIGHT // 2
BIRD_WIDTH = 51
BIRD_HEIGHT = 36
GRAVITY = 0.5
FLAP_VELOCITY = 7 	# speed up of bird

# --- TUBE ---
TUBE_WIDTH = 78     # 50
TUBE_HEIGHT = 480
TUBE_VELOCITY = 2   # Speed of tube move to the left
GATE_HEIGHT = 150	# distance of 2 tubes (tube and tube_inv)
TUBE_INTERVAL = 250	# time next tube appear


# ---------- 3. PATH & CHECKPOINTS ----------
ASSETS_DIR = "assets"
CHECKPOINTS_DIR = "checkpoints"

# Tự động tạo thư mục checkpoints nếu chưa tồn tại
os.makedirs(CHECKPOINTS_DIR, exist_ok=True)
LINEAR_CHECKPOINT = os.path.join(CHECKPOINTS_DIR, "best_bird_linear.json")
MLP_CHECKPOINT    = os.path.join(CHECKPOINTS_DIR, "best_bird_mlp.json")

# ---------- 4. AI & GA CONFIG ----------
# Model 1: Linear Perceptron
class LinearConfig:
    IN_FEATURES = 5
    OUT_FEATURES = 1
    # 5 trọng số (weights) + 1 độ lệch (bias) = 6 tham số:
    NUM_PARAMETERS = 6
    POP_SIZE = 100
    MUTATION_RATE = 0.1
    MUTATION_SIGMA = 0.3
    CHECKPOINT_FILE = LINEAR_CHECKPOINT
	
# Model 2: MLP - Multi-Layer Perceptron
class MlpConfig:
    IN_FEATURES = 5
    HIDDEN_1 = 8
    HIDDEN_2 = 4
    OUT_FEATURES = 1
    # 5*8 + 8 + 8*4 + 4 + 4*1 + 1 = 89 tham số:
    NUM_PARAMETERS = 89
    POP_SIZE = 100          # Số lượng cá thể để khám phá tốt không gian 89 gen
    MUTATION_RATE = 0.15   # Tỉ lệ đột biến gen
    MUTATION_SIGMA = 0.2   # Độ lệch chuẩn đột biến nhỏ hơn để hội tụ tốt
    CHECKPOINT_FILE = MLP_CHECKPOINT

