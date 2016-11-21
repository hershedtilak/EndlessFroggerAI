import pygame
from collections import defaultdict
from global_vars import *
import random
import math

WEIGHTS_FILE = 'weights.txt'

class froggerController:
    def getAction(self, state): raise NotImplementedError("Override me")
    def incorporateFeedback(self, state, action, reward, newState): pass
    def loadWeights(self, file_name): pass
    def saveWeights(self, file_name): pass

class humanController(froggerController):

    def __init__(self):
        self.id = "humanController"

    def getAction(self, state):
            pygame.event.pump()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                return "LEFT"
            elif keys[pygame.K_RIGHT]:
                return "RIGHT"
            elif keys[pygame.K_UP]:
                return "UP"
            elif keys[pygame.K_DOWN]:
                return "DOWN"
            elif keys[pygame.K_ESCAPE]:
                return "QUIT"
            else:
                return "STAY"


class baselineController(froggerController):

    def __init__(self):
        self.id = "baselineController"

    def getAction(self, state):
            pygame.event.pump()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                return "QUIT"

            up = state[0]
            left = state[1]
            down = state[2]
            right = state[3]
            
            if up != TAKEN:
                return "UP"
                
            randDir = []    
            if left != TAKEN:
                randDir.append("LEFT")
            if right != TAKEN:
                randDir.append("RIGHT")
            if len(randDir) > 0:
                return randDir[random.randint(0,len(randDir)-1)]
                
            return "DOWN"

            
class QLearningController(froggerController):
    def __init__(self, discount, featureExtractor, explorationProb=0.2):
        self.actions = ["UP", "LEFT", "DOWN", "RIGHT", "STAY"];
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = defaultdict(float)
        self.loadWeights(WEIGHTS_FILE)
        self.numIters = 0
        self.id = "QLearningController"

    def saveWeights(self, file_name):
        with open(file_name, "w") as f:
            for i in self.weights.keys():
                f.write(str(i) + ":" + str(self.weights[i]) + "\n")

    def loadWeights(self, file_name):
        with open(file_name, "r") as f:
            for line in f:
                strKey, val = line.split(":")
                key = eval(strKey)
                self.weights[key] = float(val)
        
    # Return the Q function associated with the weights and features
    def getQ(self, state, action):
        score = 0
        for f, v in self.featureExtractor(state, action):
            score += self.weights[f] * v
        return score

    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.
    def getAction(self, state):
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.saveWeights(WEIGHTS_FILE)
            return "QUIT"
        self.numIters += 1
        if random.random() < self.explorationProb:
            return random.choice(self.actions)
        else:
            return max((self.getQ(state, action), action) for action in self.actions)[1]

    # Call this function to get the step size to update the weights.z
    def getStepSize(self):
        return 1.0

    # We will call this function with (s, a, r, s'), which you should use to update |weights|.
    # Note that if s is a terminal state, then s' will be None.  Remember to check for this.
    # You should update the weights using self.getStepSize(); use
    # self.getQ() to compute the current estimate of the parameters.
    def incorporateFeedback(self, state, action, reward, newState):
        stepSize = self.getStepSize()
        Q_hat_opt = self.getQ(state, action)
        V_hat_opt = 0
        if newState != None:
            V_hat_opt = max(self.getQ(newState, a) for a in self.actions)
        scaleFactor = stepSize*(Q_hat_opt - (reward + self.discount*V_hat_opt))
        
        for f, v in self.featureExtractor(state, action):
            self.weights[f] -= scaleFactor*v

# Return a singleton list containing indicator feature for the (state, action)
# pair.  Provides no generalization.
def identityFeatureExtractor(state, action):
    featureKey = (state, action)
    featureValue = 1
    return [(featureKey, featureValue)]