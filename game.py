import pygame
from collections import deque
from row import Row
from frog import Frog
from controllers import *
import time
from global_vars import *
import random

class game:

    def __init__(self, width, height):
        self.score = 0
        self.count = 0
        self.updateInterval = 10
        self.startInterval = 1
        self.width = width
        self.height = height
        self.boardHeight = int(1.5 * height) # buffers 50% of board
        self.board = deque([], self.boardHeight)
        self.buffer = deque([])
        self.player = Frog(int(width/2), int(height-1))
        self.controller = baselineController()
        #self.controller = humanController()
        #self.controller = QLearningController(0.9, identityFeatureExtractor, 0.4)
        self.rowOptions = 2*["SAFE"] + 10*["ROAD"] + ["RIVER"]
        for i in range(0, self.boardHeight):
            self.board.append(Row(self.width, self.startInterval))
            
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
        if not self.buffer:
            type = random.randint(0,len(self.rowOptions)-1)
            self.buffer.append(Row(self.width, self.startInterval, self.rowOptions[type]))
            self.buffer.append(Row(self.width, self.startInterval, self.rowOptions[type]))
        if self.count != self.updateInterval:
            self.count = self.count + 1
            return
        self.board.append(self.buffer.popleft())
        self.player.y += 1
        self.count = 0
    
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
        RADIUS = 1
        x = self.player.x
        y = self.player.y
        basicState = [self.getBoardValue(x, y-1), self.getBoardValue(x-1, y), self.getBoardValue(x, y+1), self.getBoardValue(x+1, y)]
        advancedState = []
        for row in range(max(0, y-1), min(self.height, y+3)):
            advancedState = advancedState + self.board[row].getRow(x, RADIUS)
        # [UP, LEFT, DOWN, RIGHT, playerX, playerY, board]
        state = basicState + advancedState
        return tuple(state)
    
    def performAction(self, action):
        if action == "LEFT" and self.player.x > 0:
            self.player.x -= 1
        elif action == "RIGHT" and self.player.x < self.width - 1:
            self.player.x += 1
        elif action == "UP":
            self.player.y -= 1
            if self.player.y <= self.height / 2:
                self.count = self.updateInterval
        elif action == "DOWN" and self.player.y < self.height - 1:
            self.player.y += 1
        elif action == "QUIT":
            self.running = False
    
    def run(self):
        newState = self.getState()
        totalScore = 0
        numTrials = 0
        while self.running:

            oldState = newState
            action = self.controller.getAction(oldState)
            self.performAction(action)
            
            self.updateBoard()
            for row in self.board:
                row.update()
            self.drawGame()
            
            if self.playerIsDead():
                #self.player.x = random.randint(0, self.width-1)
                #self.player.y = random.randint(int(self.height/2), self.height-1)
                self.player.x = int(self.width / 2)
                self.player.y = int(self.height - 1)
                #totalScore += self.score
                #numTrials += 1
                #print("AVG SCORE: " + str(totalScore / numTrials))
                self.score = 0
            else:
                self.score += 1
            
            # temp reward
            reward = 1
            if action == "UP":
                reward = 5
            elif action == "LEFT" or action == "RIGHT":
                reward = 2
            if self.score == 0:
                reward = -5000
            newState = self.getState()
            self.controller.incorporateFeedback(oldState, action, reward, newState)
            
            pygame.display.flip()
            time.sleep (100.0 / 1000.0);
        
g = game(20,30)
g.run()