import pygame
import numpy as np

# --- Screen size ---
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700
FPS = 60

# --- Color ---
TEXT_COLOR  = (235, 240, 255)
NEON_PINK   = (255, 60, 170)    # chữ Game over
NEON_CYAN   = (60, 230, 255)    # chữ hướng dẫn
BIRD_COLOR = (0, 255, 0)
TUBE_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (0, 0, 0)

# -- Setting of genetic algorithm
POP_SIZE = 30
NUM_INPUTS = 5      # 5 neuron đầu vào
NUM_HIDDEN = 3      # 3 neuron lớp ẩn
NUM_OUTPUTS = 1     # 1 neuron đầu ra
NUM_PARAMETERS = 6  # Mô hình tuyến tính cũ chỉ dùng đúng 6 tham số (5 weights + 1 bias)
MUTATION_RATE = 0.5
MUTATION_SIGMA = 0.3

# --- Bird ---
BIRD_X = SCREEN_WIDTH // 5
BIRD_START_Y = SCREEN_HEIGHT // 2
BIRD_WIDTH = 51
BIRD_HEIGHT = 36
GRAVITY = 0.5
FLAP_VELOCITY = 7 	# speed up of bird

# --- Tube ---
TUBE_WIDTH = 78     # 50
TUBE_HEIGHT = 480
TUBE_VELOCITY = 2   # Speed of tube move to the left
GATE_HEIGHT = 150	# distance of 2 tubes (tube and tube_inv)
TUBE_INTERVAL = 250	# time next tube appear


class LinearConfig:
	pass
	

class MlpConfig:
    IN_FEATURES = 5
    HIDDEN_1 = 8
    HIDDEN_2 = 4
    OUT_FEATURES = 1
    # 5*8 + 8 + 8*4 + 4 + 4*1 + 1 = 89 tham số:
    NUM_PARAMETERS = 89
    POP_SIZE = 40          # 40 con chim để khám phá không gian 89 gen tốt hơn
    MUTATION_RATE = 0.15   # 15% tỉ lệ đột biến
    MUTATION_SIGMA = 0.2

