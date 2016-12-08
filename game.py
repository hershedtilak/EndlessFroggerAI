import pygame
from collections import deque
import copy
from row import Row
from frog import Frog
from base_controllers import *
from advanced_controllers import *
import time
from global_vars import *
import random
from feature_extractors import *

GATHER_CYCLE = 1000
GATHER_AVG = 15

GATHER_STATS = 1
TRAIN_MODE = 1
EXPLORATION_RATE = 0.4
CONTROLLER = SARSA_CONTROLLER
FEATURE_EXTRACTOR = betterThanBaselineFeatureExtractor

class game:

    def __init__(self, width, height, controller, weightIndex = None):
        self.justDied = False
        self.forceUpdate = False
        self.weightIndex = weightIndex
        self.localTrainMode = TRAIN_MODE or GATHER_STATS # start in train mode if GATHER_STATS
        self.setUpdateIntervals(self.localTrainMode)
        self.width = width
        self.height = height
        self.boardHeight = int(1.5 * height) # buffers 50% of board
        self.player = Frog(int(width/2), int(height-1))
        self.controller = controller
        self.controller.loadWeights()
        self.rowOptions = 2*["SAFE"] + 10*["ROAD"] + ["RIVER"]
        
        # open logging file
        if GATHER_STATS:
            self.logfile = open('log.txt', 'w')
            self.logfile.write("TRAINING DATA FOR " + self.controller.id.upper() + " USING " + FEATURE_EXTRACTOR.__name__.upper() + "\n")
        
        # initialize game
        self.startNewGame()
        
        # for drawing
        self.surf = pygame.display.set_mode((self.width*BLOCK_SIZE, self.height*BLOCK_SIZE), pygame.HWSURFACE)
        pygame.font.init()
        self.score_font = pygame.font.SysFont("monospace", 20)
        
        # set game to running
        self.running = True

    def startNewGame(self):
        self.score = 0
        self.count = 0

        self.player.x = int(self.width / 2)
        self.player.y = int(self.height - 1)
        
        self.board = deque([], self.boardHeight)
        self.buffer = deque([])

        self.board.append(Row(self.width, random.randint(max(1, self.rowInterval - int(self.score / 100)), self.rowInterval)))
        self.board.append(Row(self.width, random.randint(max(1, self.rowInterval - int(self.score / 100)), self.rowInterval)))
        self.board.append(Row(self.width, random.randint(max(1, self.rowInterval - int(self.score / 100)), self.rowInterval)))
        self.board.append(Row(self.width, random.randint(max(1, self.rowInterval - int(self.score / 100)), self.rowInterval)))
        for i in range(4, self.boardHeight):
            if i % 2 == 0:
                type = random.choice(self.rowOptions)
            self.board.append(Row(self.width, random.randint(max(1, self.rowInterval - int(self.score / 100)), self.rowInterval), type))

    def setUpdateIntervals(self, trainMode):
        if trainMode:
            self.updateInterval = 20
            self.controllerUpdateInterval = 2
            self.rowInterval = 2
            self.loopInterval = 1.0 / 3000.0
        else:
            self.updateInterval = 100
            self.controllerUpdateInterval = 10
            self.rowInterval = 15
            self.loopInterval = 10.0 / 1000.0
    
    def drawScores(self):
        score_string = "Score: " + str(self.score)
        scoretext = self.score_font.render(score_string, 1, (0,0,0))
        self.surf.blit(scoretext, scoretext.get_rect())
        
    def drawGame(self):
        for row in range(0, self.height):
            self.board[row].drawRow(self.surf, self.height - 1 - row)
        self.player.drawPlayer(self.surf)
        self.drawScores()
            
    def updateBoard(self):
        # update rows
        for i in range(0, self.boardHeight):
            if self.board[i].update():
                # player moves with logs
                if i == (self.height - 1 - self.player.y) and self.board[i].getType() == "RIVER":
                    shift = 2*(self.board[i].getDir() == DIR_RIGHT) - 1
                    self.player.x += shift*(self.player.x + shift >= 0 and self.player.x + shift < self.width)
        # handle board scrolling
        if not self.buffer:
            type = random.randint(0,len(self.rowOptions)-1)
            self.buffer.append(Row(self.width, random.randint(max(1, self.rowInterval - int(self.score / 100)), self.rowInterval), self.rowOptions[type]))
            self.buffer.append(Row(self.width, random.randint(max(1, self.rowInterval - int(self.score / 100)), self.rowInterval), self.rowOptions[type]))
        if self.count <= max(self.rowInterval, (self.updateInterval / max(1, (self.score / 100)))) and self.forceUpdate == False:
            self.count = self.count + 1
            return
        self.board.append(self.buffer.popleft())
        self.player.y += 1
        self.count = 0
        self.forceUpdate = False
    
    def getBoardValue(self, x, y):
        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            return self.board[self.height - 1 - y].getValue(x)
        return -1
    
    def boardValueOpen(self, x, y):
        val = self.getBoardValue(x, y)
        return (val != TAKEN and val != -1)
    
    def getRowFromPlayerCoords(self, y, board):
        return board[self.height - 1 - y]
    
    def getRowInfoFromPlayerCoords(self, y, board):
        row = self.getRowFromPlayerCoords(y, board)
        return [row.getType(), row.getDir(), row.getSinkCounter()]
            
    def playerIsDead(self):
        if self.player.y >= self.height:
            return True
        if self.getBoardValue(self.player.x, self.player.y) == 1:
            return True
        return False
    
    def getState(self):
        x = self.player.x
        y = self.player.y
        basicState = [self.getBoardValue(x, y-1), self.getBoardValue(x-1, y), self.getBoardValue(x, y+1), self.getBoardValue(x+1, y), self.getBoardValue(x, y)]
        return tuple((basicState, x, y, self.justDied, self, copy.deepcopy(self.board)))
    
    def performAction(self, action):
        if action == "LEFT" and self.player.x > 0:
            self.player.x -= 1
        elif action == "RIGHT" and self.player.x < self.width - 1:
            self.player.x += 1
        elif action == "UP":
            self.player.y -= 1
            if self.player.y <= self.height / 2:
                self.forceUpdate = True
        elif action == "DOWN" and self.player.y < self.height - 1:
            self.player.y += 1
        elif action == "QUIT":
            self.running = False
    
    def getReward(self, action):
        reward = 7 * (action == "UP")
        reward -= 9 * (action == "DOWN")
        type, dir, sinkCounter = self.getRowInfoFromPlayerCoords(self.player.y - 1, self.board)
        if type == "RIVER":
            row = self.getRowFromPlayerCoords(self.player.y - 1, self.board)
            dist = row.getDistToClosestLog(self.player.x)
            reward += int(0.25*(self.width - dist))
        type, dir, sinkCounter = self.getRowInfoFromPlayerCoords(min(self.height - 1, self.player.y + 1), self.board)
        if type == "RIVER":
            reward += 5
        return reward
    
    def run(self):
        newState = self.getState()
        totalScore = 0
        numTrials = 27000
        numCycles = 1
        save = 1
        printedScore = False
        while self.running:

            # improve responsiveness of human controller
            if CONTROLLER is HUMAN_CONTROLLER:
                self.controller.updateAction()
                
            if (numCycles % self.controllerUpdateInterval == 1) or (self.justDied == True):
                oldState = newState
                if self.justDied == True:
                    newState = None
                    if self.localTrainMode:
                        self.controller.incorporateFeedback(oldState, action, DEATH_STATE_REWARD, newState)
                    self.justDied = False
                    self.startNewGame()
                    oldState = self.getState()

                if CONTROLLER is GENETIC_CONTROLLER:
                    action = self.controller.getAction(oldState, self.weightIndex)
                else:
                    action = self.controller.getAction(oldState)

                self.performAction(action)
            
            # update board
            self.updateBoard()
  
            if self.playerIsDead():
                if CONTROLLER is GENETIC_CONTROLLER:
                    self.running = False
                    return self.score
                self.justDied = True
            else:
                if numCycles % (0.1 / self.loopInterval) == 0:
                    self.score += 1
            
            # draw board
            if not self.localTrainMode:
                self.drawGame()
            
            # get new state and reward
            newState = self.getState() 
            reward = self.getReward(action)
            if self.localTrainMode and ((numCycles % self.controllerUpdateInterval == 0) or (self.justDied == True)):
                self.controller.incorporateFeedback(oldState, action, reward, newState)
            
            if self.justDied and GATHER_STATS:
                # start generating statistics if GATHER_STATS
                numTrials += 1
                totalScore += self.score   
                if numTrials % GATHER_CYCLE == 0:
                    totalScore = 0
                    self.logfile.write("Trained for " + str(numTrials) + " trials\n")
                    self.logfile.flush()
                    self.localTrainMode = False
                    self.setUpdateIntervals(self.localTrainMode)
                    self.controller.setExplorationRate(0)
                    printedScore = False
                if numTrials % GATHER_CYCLE == GATHER_AVG and printedScore == False:
                    self.logfile.write("Avg Score for " + str(GATHER_AVG) + " trials: " + str(1.0 * totalScore / GATHER_AVG) + "\n")
                    self.logfile.flush()
                    numTrials -= GATHER_AVG
                    self.localTrainMode = True
                    self.setUpdateIntervals(self.localTrainMode)
                    self.controller.setExplorationRate(EXPLORATION_RATE)
                    printedScore = True    
                # end generating statistics
            
            
            if numCycles % 10000 == 1:
                if save == 1:
                    self.controller.saveWeights()
                    save = 0
            elif save == 0:
                save = 1
            
            numCycles += 1
            
            if not self.localTrainMode:
                pygame.display.flip()
            
            time.sleep (self.loopInterval);
            
        if GATHER_STATS:
            self.logfile.close()

if CONTROLLER == GENETIC_CONTROLLER:
    n = 4
    mutationProb = 0.1
    mutationSTD = 2
    controller = geneticAlgorithmController(n, FEATURE_EXTRACTOR, mutationProb, mutationSTD)
    # Greg's stuff
    #instantiate n games
    #after all games done update the weights  
    numIters = 2
    iters = 0
    
    geneticLog = open('log.txt', 'w')
    geneticLog.write("TRAINING DATA FOR GENETIC ALGORITHM USING " + FEATURE_EXTRACTOR.__name__.upper() + "\n")
    
    while(iters < numIters):
        for index in range(n):
            g = game(20,30, controller, index)
            controller.fitness.append(g.run())
            geneticLog.write("SCORE OF MOST FIT GENE: " + str(max(controller.fitness)))
            geneticLog.flush()
            controller.reproduce()
        iters += 1
    
    geneticLog.close()


else:          
    if CONTROLLER == HUMAN_CONTROLLER:
        controller = humanController()
    elif CONTROLLER == BASELINE_CONTROLLER:
        controller = baselineController()
    elif CONTROLLER == QLEARNING_CONTROLLER:
        controller = QLearningController(0.8, FEATURE_EXTRACTOR, EXPLORATION_RATE * TRAIN_MODE)  
    elif CONTROLLER == SARSA_CONTROLLER:
        controller = SARSAController(0.8, FEATURE_EXTRACTOR, EXPLORATION_RATE * TRAIN_MODE)  
    g = game(20,30, controller)
    g.run()