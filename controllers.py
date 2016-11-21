import pygame
from collections import defaultdict
from global_vars import *
import random
import math

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

            basicState = state[0]
            up = basicState[0]
            left = basicState[1]
            down = basicState[2]
            right = basicState[3]
            
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
        self.weights_file_name = 'weights_' + featureExtractor.__name__ + '.txt'
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = defaultdict(float)
        self.loadWeights()
        self.numIters = 0
        self.id = "QLearningController"

    def saveWeights(self):
        with open(self.weights_file_name, "w") as f:
            for i in self.weights.keys():
                f.write(str(i) + ":" + str(self.weights[i]) + "\n")

    def loadWeights(self):
        with open(self.weights_file_name, "r") as f:
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
            self.saveWeights()
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

# Features detailing safety of moves
def safetyFeatureExtractor(state, action):
    basicState = state[0]
    x = state[1]
    y = state[2]
    game = state[3]

    #front safe
    front_isOpen = (basicState[0] != TAKEN) and (basicState[0] != -1)
    if front_isOpen:
        front_rowDir = game.board[y-1].getDir()
        front_isSafe = (front_rowDir == DIR_LEFT and game.getBoardValue(x+1, y-1) != TAKEN and game.getBoardValue(x+1, y-1) != -1) or \
        (front_rowDir == DIR_RIGHT and game.getBoardValue(x-1, y-1) != TAKEN and game.getBoardValue(x-1, y-1) != -1)
    move_Forward = 1*(front_isOpen and front_isSafe)
    forward_sinkTimer = 1*(game.board[y-1].getSinkCounter() == SINK_WARN_TIME - 1 )
    #back safe
    back_isOpen = (basicState[2] != TAKEN) and (basicState[2] != -1)
    if back_isOpen:
        back_rowDir = game.board[y+1].getDir()
        back_isSafe = (back_rowDir == DIR_LEFT and game.getBoardValue(x+1, y+1) != TAKEN and game.getBoardValue(x+1, y+1) != -1) or \
        (back_rowDir == DIR_RIGHT and game.getBoardValue(x-1, y+1) != TAKEN and game.getBoardValue(x-1, y+1) != -1)
    move_Backward = 1*(back_isOpen and back_isSafe)
    backward_sinkTimer = 1*(game.board[y+1].getSinkCounter() == SINK_WARN_TIME - 1)
    #left safe
    left_isOpen = (basicState[1] != TAKEN) and (basicState[1] != -1)
    if left_isOpen:
        left_rowDir = game.board[y].getDir()
        left_isSafe = (left_rowDir == DIR_RIGHT and game.getBoardValue(x-2, y) != TAKEN and game.getBoardValue(x-2, y) != -1)
    move_Left = 1*(left_isOpen and left_isSafe)
    #right safe
    right_isOpen = (basicState[3] != TAKEN) and (basicState[3] != -1)
    if right_isOpen:
        right_rowDir = game.board[y].getDir()
        right_isSafe = (right_rowDir == DIR_LEFT and game.getBoardValue(x+2, y) != TAKEN and game.getBoardValue(x+2, y) != -1)
    move_Right = 1*(right_isOpen and right_isSafe)
    left_right_sinkTimer = 1*(game.board[y].getSinkCounter() == SINK_WARN_TIME - 1)
    
    advancedState = basicState + [move_Forward, move_Backward, move_Left, move_Right, forward_sinkTimer, backward_sinkTimer, left_right_sinkTimer]
    
    featureKey = (tuple(advancedState), action)
    featureValue = 1
    return [(featureKey, featureValue)]
    
# larger feature extractor
def moreInfoFeatureExtractor(state, action):
    basicState = state[0]
    x = state[1]
    y = state[2]
    game = state[3]

    RADIUS = 1
    advancedState = []
    for row in range(max(0, y-1), min(game.height, y+2)):
        advancedState = advancedState + game.board[row].getRow(x, RADIUS) + [game.board[row].getDir()] + [game.board[row].getSinkCounter()]
    
    # [UP, LEFT, DOWN, RIGHT, playerX, playerY, board]
    featureKey = (tuple(basicState + advancedState), action)
    featureValue = 1
    return [(featureKey, featureValue)]