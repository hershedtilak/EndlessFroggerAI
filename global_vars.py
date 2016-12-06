import pygame

BLOCK_SIZE = 20
fontColor = pygame.Color(0,0,0)
frogColor = pygame.Color(255,0,255)
TAKEN = 1

carColor = pygame.Color(255,0,0)
riverColor = pygame.Color(0,0,255)
logColor = pygame.Color(150,110,110)
sinkingLogColor = pygame.Color(0,0,0)
roadColor = pygame.Color(150,150,150)
grassColor = pygame.Color(0,128,0)

SINK_WARN_TIME = 3
DIR_LEFT = 0
DIR_RIGHT = 1
DIR_UP = 2

HUMAN_CONTROLLER = 0
BASELINE_CONTROLLER = 1
QLEARNING_CONTROLLER = 2
SARSA_CONTROLLER = 3
GENETIC_CONTROLLER = 4

DEATH_STATE_REWARD = -200