import pygame
from global_vars import *


class Frog:
    scale = 0.5
    
    def __init__(self, startX, startY):
        self.x = int(startX)
        self.y = int(startY)
        
    def isDead(self):
        return (self.y < 0)
        
    def drawPlayer(self, surface):
        surface.fill(frogColor, pygame.Rect((self.x*BLOCK_SIZE + ((1-Frog.scale)*BLOCK_SIZE/2), self.y*BLOCK_SIZE + ((1-Frog.scale)*BLOCK_SIZE/2)), (Frog.scale*BLOCK_SIZE, Frog.scale*BLOCK_SIZE)))
        
        
