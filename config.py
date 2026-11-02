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
NUM_INPUTS = 5     # number input of no ron
NUM_PARAMETERS = 6
MUTATION_RATE = 0.1
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


