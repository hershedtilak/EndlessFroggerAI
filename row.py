import pygame
from collections import deque
import random
from global_vars import *

class Row:
    def __init__(self, length, interval, type="SAFE"):
        self.count = 0
        self.interval = (interval * (type == "ROAD")) + (2 * interval * (type == "RIVER"))
        self.len = length
        self.type = type
        self.dir = random.randint(0,1)
        self.rowQ = deque([1 * (self.type == "RIVER")] * self.len, self.len)
        self.buffer = deque([])
        
        if type == "RIVER":
            self.oneColor = riverColor
            self.zeroColor = logColor
        elif type == "ROAD":
            self.oneColor = carColor
            self.zeroColor = roadColor
        else:
            self.zeroColor = grassColor
            self.oneColor = grassColor
        
    def drawRow(self, surface, rowNum):
        for col in range(0, self.len):
            if self.rowQ[col]:
                color = self.oneColor
            else:
                color = self.zeroColor
            surface.fill(color, pygame.Rect((col*BLOCK_SIZE, rowNum*BLOCK_SIZE), (BLOCK_SIZE, BLOCK_SIZE)))

    def getValue(self, col):
        return self.rowQ[col]

    def getRow(self, centerX, radius):
        return list(self.rowQ)[max(0, centerX-radius):min(self.len, centerX+radius+1)]
        
    def update(self):
        if self.count != self.interval:
            self.count = self.count + 1
            return
        if not self.buffer:
            self.fillbuffer()
        if self.dir == 0:
            self.rowQ.append(self.buffer.popleft())
        else:
            self.rowQ.appendleft(self.buffer.popleft())
        self.count = 0
            
    def fillbuffer(self):
        p = random.randint(0,20)
        if p <= (0 * (self.type == "ROAD") + 10 * (self.type == "RIVER")):
            self.buffer.append(1 * (self.type == "ROAD"))
            self.buffer.append(1 * (self.type == "ROAD"))
            self.buffer.append(1 * (self.type == "ROAD"))
            if self.type == "RIVER":
                self.buffer.append(1 * (self.type == "ROAD"))
            
        self.buffer.append(1 * (self.type == "RIVER"))
        self.buffer.append(1 * (self.type == "RIVER"))
        
