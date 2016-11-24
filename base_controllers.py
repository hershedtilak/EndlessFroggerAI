import pygame
from global_vars import *
import random

class froggerController:
    def getAction(self, state): raise NotImplementedError("Override me")
    def incorporateFeedback(self, state, action, reward, newState): pass
    def loadWeights(self): pass
    def saveWeights(self): pass

class humanController(froggerController):
    id = "humanController"

    def __init__(self):
        self.lastAction = "STAY"

    def updateAction(self):
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.lastAction = "LEFT"
        elif keys[pygame.K_RIGHT]:
            self.lastAction = "RIGHT"
        elif keys[pygame.K_UP]:
            self.lastAction = "UP"
        elif keys[pygame.K_DOWN]:
            self.lastAction = "DOWN"
        elif keys[pygame.K_ESCAPE]:
            self.lastAction = "QUIT"
 
    def getAction(self, state):
        retVal = self.lastAction
        self.lastAction = "STAY"
        return retVal


class baselineController(froggerController):

    id = "baselineController"
    
    def getAction(self, state):
            pygame.event.pump()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                return "QUIT"

            basicState = state[0]
            up = basicState[0]
            left = basicState[1]
            down = basicState[2]
            right = basicState[3]
            
            if up != TAKEN:
                return "UP"
            return "STAY"   
            randDir = []    
            if left != TAKEN:
                randDir.append("LEFT")
            if right != TAKEN:
                randDir.append("RIGHT")
            if len(randDir) > 0:
                return randDir[random.randint(0,len(randDir)-1)]
                
            return "DOWN"

