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
        file_name = 'weights/weights_' + self.id + '_' + self.featureExtractor.__name__ + '.txt'
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
        #return 1.0 / math.sqrt(self.numIters)
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
        #return 1.0 / math.sqrt(self.numIters)
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

    def __init__(self, sizeOfGenome, featureExtractor, mutationProb, mutationSTD):
        self.actions = ["UP", "LEFT", "DOWN", "RIGHT", "STAY"]
        self.featureExtractor = featureExtractor
        self.mutationProb = mutationProb
        self.mutationSTD = mutationSTD
        self.sizeOfGenome = sizeOfGenome
        self.weights = [defaultdict(float)] * sizeOfGenome
        self.fitness = [] * sizeOfGenome
        self.numIters = 0

    # Return the Q function associated with the weights and features
    def getQ(self, state, action, index):
        score = 0
        print(index)
        for f, v in self.featureExtractor(state, action):
            if f in self.weights[index]:
                score += self.weights[index][f] * v
        return score
        
    # Get an action - uses exploration probability
    def getAction(self, state, index):
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.saveWeights()
            return "QUIT"
        self.numIters += 1

        return max((self.getQ(state, action, index), action) for action in self.actions)[1]

    def getStepSize(self):
        #return 1.0 / math.sqrt(self.numIters)
        return 0.05

    def reproduce(self):

        #first sort the weight vectors by fitness
        sortedWeightInds = [i[0] for i in sorted(enumerate(self.fitness), key=lambda x:x[1])]
        sortedWeightInds.reverse()
        allParentsSorted = [self.weights[sortedWeightInds[i]] for i in range(self.sizeOfGenome)]
        #take the top sqrt(n) weights
        topSqrtN = int(math.sqrt(self.sizeOfGenome))
        topParents = allParentsSorted[0:topSqrtN]

        #do all possible weighted linear combinations
        for i in range(len(topParents)):
            for j in range(i + 1, len(topParents)):
                fitI = self.fitness[sortedWeightInds[i]]
                fitJ = self.fitness[sortedWeightInds[j]]
                totalFitness = fitI + fitJ
                weightsI = topParents[i]
                weightsJ = topParents[j]
                print("WeightsI" , weightsI)
                print("WeightsJ" , weightsJ)
                children = []
                weightedCombo = {}
                for key in weightsI:
                    if key in weightsJ:
                        weightedCombo[key] = (fitI * weightsI[key] + fitJ * weightsJ[key]) / totalFitness
                    else:
                        weightedCombo[key] = fitI * weightsI[key] / totalFitness
                for key in weightsJ:
                    if key not in weightsI:
                        weightedCombo[key] = fitJ * weightsJ[key] / totalFitness
                print("Weighted Comobo")
                print(weightedCombo)
                randKey = random.choice(list(weightedCombo.keys()))
                if self.mutationProb > random.random():
                    weightedCombo[randKey] += random.gauss(0, self.mutationSTD)


                children.append(weightedCombo)

        extras = self.sizeOfGenome - len(children)
        for i in range(extras):
            children.append(allParentsSorted[i])
        print(self.weights)
        self.weights = children

    def saveWeights(self): pass

    def loadWeights(self): pass




