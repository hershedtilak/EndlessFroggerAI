import pygame
from collections import deque
from row import Row
from frog import Frog
from controllers import *
import time
from global_vars import *
import random
from feature_extractors import *

TRAIN_MODE = 1
HUMAN_CONTROLLER = 0

class game:

    def __init__(self, width, height):
        self.score = 0
        self.count = 0
        self.forceUpdate = False
        self.updateInterval = 100
        self.controllerUpdateInterval = 10
        self.rowInterval = 15
        self.loopInterval = 10.0 / 1000.0
        self.controllerExplorationRate = 0.0
        if TRAIN_MODE:
            self.updateInterval = 10
            self.controllerUpdateInterval = 1
            self.rowInterval = 1
            self.loopInterval = 2.0 / 1000.0
            self.controllerExplorationRate = 0.4
        self.width = width
        self.height = height
        self.boardHeight = int(1.5 * height) # buffers 50% of board
        self.board = deque([], self.boardHeight)
        self.buffer = deque([])
        self.player = Frog(int(width/2), int(height-1))
        if HUMAN_CONTROLLER:
            self.controller = humanController()
        else:
            #self.controller = baselineController()
            self.controller = QLearningController(0.9, safetyFeatureExtractor, self.controllerExplorationRate)
        self.rowOptions = 2*["SAFE"] + 10*["ROAD"] + ["RIVER"]
        for i in range(0, self.boardHeight):
            self.board.append(Row(self.width, random.randint(max(1, self.rowInterval - int(self.score / 10)), self.rowInterval)))
            
        # for drawing
        self.surf = pygame.display.set_mode((self.width*BLOCK_SIZE, self.height*BLOCK_SIZE), pygame.HWSURFACE)
        pygame.font.init()
        self.score_font = pygame.font.SysFont("monospace", 20)
        
        # set game to running
        self.running = True

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
            self.buffer.append(Row(self.width, random.randint(max(1, self.rowInterval - int(self.score / 10)), self.rowInterval), self.rowOptions[type]))
            self.buffer.append(Row(self.width, random.randint(max(1, self.rowInterval - int(self.score / 10)), self.rowInterval), self.rowOptions[type]))
        if self.count <= (self.updateInterval / max(1, (self.score / 10))) and self.forceUpdate == False:
            self.count = self.count + 1
            return
        self.board.append(self.buffer.popleft())
        self.player.y += 1
        self.count = 0
        self.forceUpdate = False
    
    def getBoardValue(self, x, y):
        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            return self.board[self.height - 1 - y].getValue(x)
        else:
            return -1
    
    def playerIsDead(self):
        if self.player.y >= self.height:
            return True
        if self.getBoardValue(self.player.x, self.player.y) == 1:
            return True
        return False
    
    def getState(self):
        x = self.player.x
        y = self.player.y
        basicState = [self.getBoardValue(x, y-1), self.getBoardValue(x-1, y), self.getBoardValue(x, y+1), self.getBoardValue(x+1, y)]
        return tuple((basicState, x, y, self))
    
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
    
    def run(self):
        newState = self.getState()
        totalScore = 0
        numCycles = 0
        save = 1
        while self.running:

            # improve responsiveness of human controller
            if HUMAN_CONTROLLER:
                self.controller.updateAction()
        
            if numCycles % self.controllerUpdateInterval == 0:
                oldState = newState
                action = self.controller.getAction(oldState)
                self.performAction(action)
            
            # update board
            self.updateBoard()
                
            self.drawGame()
            
            newState = self.getState()
            
            reward = 0
            if action == "UP":
                reward = 2
            elif action == "LEFT" or action == "RIGHT" or action == "STAY":
                reward = 1
    
            if self.playerIsDead():
                #self.player.x = random.randint(0, self.width-1)
                #self.player.y = random.randint(int(self.height/2), self.height-1)
                self.player.x = int(self.width / 2)
                self.player.y = int(self.height - 1)
                #totalScore += self.score
                #print("AVG SCORE: " + str(totalScore / numCycles))
                self.score = 0
                reward = -1000
            else:
                if numCycles % (1.0 / self.loopInterval) == 0:
                    self.score += 1
                        
            self.controller.incorporateFeedback(oldState, action, reward, newState)
            
            if numCycles % 10000 == 1:
                if save == 1:
                    self.controller.saveWeights()
                    save = 0
            elif save == 0:
                save = 1
            
            numCycles += 1
            pygame.display.flip()
            time.sleep (self.loopInterval);
        
g = game(20,30)
g.run()