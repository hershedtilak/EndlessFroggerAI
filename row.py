import pygame
from collections import deque
import random
from global_vars import *

class Row:
    def __init__(self, length, interval, type="SAFE"):
        self.count = 0
        self.sinkingLog = False
        self.sinkCounter = 0
        self.interval = (interval * (type == "ROAD")) + (2 * interval * (type == "RIVER"))
        self.len = length
        self.type = type
        self.dir = random.randint(0,1)
        self.rowQ = deque([1 * (self.type == "RIVER")] * self.len, self.len)
        self.buffer = deque([])
        
        if type == "RIVER":
            self.oneColor = riverColor
            self.pointFiveColor = sinkingLogColor
            self.zeroColor = logColor
        elif type == "ROAD":
            self.oneColor = carColor
            self.zeroColor = roadColor
        else:
            self.zeroColor = grassColor
            self.oneColor = grassColor
        
    def drawRow(self, surface, rowNum):
        for col in range(0, self.len):
            if self.rowQ[col] == 1:
                color = self.oneColor
            elif self.rowQ[col] == 0.5:
                color = self.pointFiveColor
            else:
                color = self.zeroColor
            surface.fill(color, pygame.Rect((col*BLOCK_SIZE, rowNum*BLOCK_SIZE), (BLOCK_SIZE, BLOCK_SIZE)))

    def getValue(self, col):
        return self.rowQ[col]

    def getValues(self, centerX, radius):
        return list(self.rowQ)[max(0, centerX-radius):min(self.len, centerX+radius+1)]
        
    def getDir(self):
        return self.dir
        
    def getSinkCounter(self):
        return self.sinkCounter

    def getType(self):
        return self.type
     
    def getDistToClosestLog(self, x):
        offset = 0
        while self.rowQ[min(x + offset, self.len - 1)] == 1 and self.rowQ[max(0, x - offset)] == 1:
            offset += 1
            if offset == self.len:
                return -1
        return offset
     
    def getDirOfClosestLog(self, x):
        offset = 0
        while self.rowQ[min(x + offset, self.len - 1)] == 1 and self.rowQ[max(0, x - offset)] == 1:
            offset += 1
            if offset == self.len:
                return self.len
        if offset == 0:
            return DIR_UP
        if self.rowQ[min(x + offset, self.len - 1)] != 1:
            return DIR_RIGHT
        return DIR_LEFT
     
    def clearRow(self):
        for i in range(0, self.len):
            self.rowQ[i] = 0
    
    # returns whether or not the row was updated
    def update(self):
        if self.count != self.interval:
            self.count = self.count + 1
            return False
        if not self.buffer:
            self.fillbuffer()
        if self.dir == DIR_LEFT:
            self.rowQ.append(self.buffer.popleft())
        else:
            self.rowQ.appendleft(self.buffer.popleft())
        self.count = 0
        
        # sink a log
        if self.type == "RIVER" and self.sinkingLog == False:
            index = random.randint(0, self.len-4)
            if self.rowQ[index] == 0 and self.rowQ[index + 1] == 0 and self.rowQ[index + 2] == 0 and self.rowQ[index + 3] == 0:
                self.rowQ[index] = 0.5
                self.rowQ[index + 1] = 0.5
                self.rowQ[index + 2] = 0.5
                self.rowQ[index + 3] = 0.5
                self.sinkingLog = True
                self.sinkCounter = 0
        elif self.sinkingLog == True:
            self.sinkCounter += 1
            if self.sinkCounter == SINK_WARN_TIME:
                for i in range(0, self.len):
                    self.rowQ[i] = int(self.rowQ[i] + 0.5)
                self.sinkingLog = False
                
        return True
            
    def fillbuffer(self):
        p = random.randint(0,20)
        if p <= (0 * (self.type == "ROAD") + 10 * (self.type == "RIVER")):
            self.buffer.extend([1, 1] * (self.type == "ROAD"))
            self.buffer.extend([0, 0, 0, 0] * (self.type == "RIVER"))
            
        self.buffer.append(1 * (self.type == "RIVER"))
        self.buffer.append(1 * (self.type == "RIVER"))
        
