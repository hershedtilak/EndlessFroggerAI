from global_vars import *

# Features detailing safety of moves
def safetyFeatureExtractor(state, action):
    basicState = state[0]
    x = state[1]
    y = state[2]
    game = state[3]

    #front safe
    front_isOpen = (basicState[0] != TAKEN) and (basicState[0] != -1)
    if front_isOpen:
        front_rowDir = game.getRowDir(y-1)
        front_isSafe = (front_rowDir == DIR_LEFT and game.getBoardValue(x+1, y-1) != TAKEN and game.getBoardValue(x+1, y-1) != -1) or \
        (front_rowDir == DIR_RIGHT and game.getBoardValue(x-1, y-1) != TAKEN and game.getBoardValue(x-1, y-1) != -1)
    move_Forward = 1*(front_isOpen and front_isSafe)
    forward_sinkTimer = 1*(game.getRowSinkCounter(y-1) == SINK_WARN_TIME - 1)
    #back safe
    back_isOpen = (basicState[2] != TAKEN) and (basicState[2] != -1)
    if back_isOpen:
        back_rowDir = game.getRowDir(y+1)
        back_isSafe = (back_rowDir == DIR_LEFT and game.getBoardValue(x+1, y+1) != TAKEN and game.getBoardValue(x+1, y+1) != -1) or \
        (back_rowDir == DIR_RIGHT and game.getBoardValue(x-1, y+1) != TAKEN and game.getBoardValue(x-1, y+1) != -1)
    move_Backward = 1*(back_isOpen and back_isSafe)
    backward_sinkTimer = 1*(game.getRowSinkCounter(y+1) == SINK_WARN_TIME - 1)
    #left safe
    left_isOpen = (basicState[1] != TAKEN) and (basicState[1] != -1)
    if left_isOpen:
        left_rowDir = game.getRowDir(y)
        left_isSafe = (left_rowDir == DIR_RIGHT and game.getBoardValue(x-2, y) != TAKEN and game.getBoardValue(x-2, y) != -1)
    move_Left = 1*(left_isOpen and left_isSafe)
    #right safe
    right_isOpen = (basicState[3] != TAKEN) and (basicState[3] != -1)
    if right_isOpen:
        right_rowDir = game.getRowDir(y)
        right_isSafe = (right_rowDir == DIR_LEFT and game.getBoardValue(x+2, y) != TAKEN and game.getBoardValue(x+2, y) != -1)
    move_Right = 1*(right_isOpen and right_isSafe)
    left_right_sinkTimer = 1*(game.getRowSinkCounter(y) == SINK_WARN_TIME - 1)
    
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
        advancedState = advancedState + game.getRow(row).getValues(x, RADIUS) + [game.getRowDir(row)] + [game.getRowSinkCounter(row)]
    
    # [UP, LEFT, DOWN, RIGHT, playerX, playerY, board]
    featureKey = (tuple(basicState + advancedState), action)
    featureValue = 1
    return [(featureKey, featureValue)]