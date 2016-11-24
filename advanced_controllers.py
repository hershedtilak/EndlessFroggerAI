import pygame
from collections import defaultdict
from global_vars import *
from base_controllers import *
import random
import math
import os.path

class advancedFroggerController(froggerController):
    def getAction(self, state): raise NotImplementedError("Override me")
    def incorporateFeedback(self, state, action, reward, newState): pass
    
    def saveWeights(self):
        file_name = 'weights/weights_' + self.id + '_' + self.featureExtractor.__name__ + '.txt'
        with open(file_name, "w") as f:
            for i in self.weights.keys():
                f.write(str(i) + ":" + str(self.weights[i]) + "\n")

    def loadWeights(self):
        file_name = 'weights/weights_' + self.featureExtractor.__name__ + '_' + self.id + '.txt'
        if os.path.isfile(file_name):
            with open(file_name, "r") as f:
                for line in f:
                    strKey, val = line.split(":")
                    key = eval(strKey)
                    self.weights[key] = float(val)


            
class QLearningController(advancedFroggerController):
    
    id = "QLearningController"

    def __init__(self, discount, featureExtractor, explorationProb=0.2):
        self.actions = ["UP", "LEFT", "DOWN", "RIGHT", "STAY"]
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = defaultdict(float)
        self.loadWeights()
        self.numIters = 0
    
    # Return the Q function associated with the weights and features
    def getQ(self, state, action):
        score = 0
        for f, v in self.featureExtractor(state, action):
            score += self.weights[f] * v
        return score

    # Get the optimal action (or a random action with set probability)
    def getAction(self, state):
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.saveWeights()
            return "QUIT"
        self.numIters += 1
        if random.random() < self.explorationProb:
            return random.choice(self.actions)
        else:
            return max((self.getQ(state, action), action) for action in self.actions)[1]

    def getStepSize(self):
        return 1.0 / math.sqrt(self.numIters)
        return 0.1

    # Update weights
    def incorporateFeedback(self, state, action, reward, newState):
        stepSize = self.getStepSize()
        Q_hat_opt = self.getQ(state, action)
        V_hat_opt = 0
        if newState != None:
            V_hat_opt = max(self.getQ(newState, a) for a in self.actions)
        scaleFactor = stepSize*(Q_hat_opt - (reward + self.discount*V_hat_opt))
        
        for f, v in self.featureExtractor(state, action):
            self.weights[f] -= scaleFactor*v

 
class SARSAController(advancedFroggerController):
    id = "SARSAController"
    
    def __init__(self, discount, featureExtractor, explorationProb=0.2):
        self.actions = ["UP", "LEFT", "DOWN", "RIGHT", "STAY"]
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = defaultdict(float)
        self.loadWeights()
        self.numIters = 0
        self.bufferedAction = None
        
    # Return the Q function associated with the weights and features
    def getQ(self, state, action):
        score = 0
        for f, v in self.featureExtractor(state, action):
            score += self.weights[f] * v
        return score

    # Get an action - uses exploration probability
    def getAction(self, state):
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.saveWeights()
            return "QUIT"
        self.numIters += 1
        
        if self.bufferedAction != None:
            retVal = self.bufferedAction
            self.bufferedAction = None
            return retVal
            
        if random.random() < self.explorationProb:
            return random.choice(self.actions)
        else:
            return max((self.getQ(state, action), action) for action in self.actions)[1]

    def getStepSize(self):
        return 1.0 / math.sqrt(self.numIters)
        return 0.1

    # Update weights
    def incorporateFeedback(self, state, action, reward, newState):
        stepSize = self.getStepSize()
        Q_hat_opt = self.getQ(state, action)
        V_hat_opt = 0
        if newState != None:
            if self.bufferedAction == None:
                self.bufferedAction = self.getAction(newState)
            V_hat_opt = self.getQ(newState, self.bufferedAction)
        scaleFactor = stepSize*(Q_hat_opt - (reward + self.discount*V_hat_opt))
        
        for f, v in self.featureExtractor(state, action):
            self.weights[f] -= scaleFactor*v
 
# FOR GREG
class geneticAlgorithmController(advancedFroggerController):
    id = "geneticAlgorithmController"

    def __init__(self):
        raise NotImplementedError("Override me")
        
    def getAction(self, state):
        raise NotImplementedError("Override me")