from global_vars import *

#test
def testFeatureExtractor(state, action):
    if state[3]:
        return [(-10, 1)]
    newState = [1 * (x == 0) for x in state[0][0:4]]
    return [((tuple(newState), action), 1)]

# Features detailing safety of moves
def safetyFeatureExtractor(state, action):
    basicState = state[0]
    x = state[1]
    y = state[2]
    justDied = state[3]
    game = state[4]

    if(justDied):
        return [(-10, 1)]
    
    #get cur values
    curType, curDir, curSinkCounter = game.getRowInfoFromPlayerCoords(y)
    
    #in bottom row
    in_bottom_row = (y == (game.height - 1))
    on_edge = (x == 0 or x == (game.width-1))
    
    #front safe
    front_exists = (basicState[0] != -1)
    if front_exists:
        type, dir, sinkCounter = game.getRowInfoFromPlayerCoords(y-1)
        if curType == "RIVER":
            front_isSafe = (curDir == dir and game.boardValueOpen(x, y-1)) or \
                (curDir != dir and game.boardValueOpen(x + 2*(curDir - dir), y-1))
        else:
            front_isSafe = (dir == DIR_LEFT and game.boardValueOpen(x+1, y-1)) or (dir == DIR_RIGHT and game.boardValueOpen(x-1, y-1))
        if type == "RIVER":
            front_willSink = (sinkCounter == SINK_WARN_TIME - 1 and basicState[0] == 0.5)
        else:
            front_willSink = False      
    move_Forward = 1*(front_exists and front_isSafe and not front_willSink and not on_edge)
    #back safe
    back_exists = (basicState[2] != -1)
    if back_exists:
        type, dir, sinkCounter = game.getRowInfoFromPlayerCoords(y+1)
        if curType == "RIVER":
            back_isSafe = (curDir == dir and game.boardValueOpen(x, y+1)) or \
                (curDir != dir and game.boardValueOpen(x + 2*(curDir - dir), y+1))
        else:
            back_isSafe = (dir == DIR_LEFT and game.boardValueOpen(x+1, y+1)) or (dir == DIR_RIGHT and game.boardValueOpen(x-1, y+1))
        if type == "RIVER":
            back_willSink = (sinkCounter == SINK_WARN_TIME - 1 and basicState[2] == 0.5)
        else:
            back_willSink = False       
    move_Backward = 1*(back_exists and back_isSafe and not back_willSink and not on_edge)
    #left safe
    left_exists = (basicState[1] != -1)
    if left_exists:
        if curType != "RIVER":
            left_isSafe = (curDir == DIR_RIGHT and game.boardValueOpen(x-2, y)) or (curDir == DIR_LEFT)
            left_willSink = False
        else:
            left_isSafe = game.boardValueOpen(x-1, y)
            left_willSink = (curSinkCounter == SINK_WARN_TIME - 1 and basicState[1] == 0.5)     
    move_Left = 1*(left_exists and left_isSafe and not left_willSink and not in_bottom_row)
    #right safe
    right_exists = game.boardValueOpen(x+1, y)
    if right_exists:
        if curType != "RIVER":
            right_isSafe = (curDir == DIR_LEFT and game.boardValueOpen(x+2, y)) or (curDir == DIR_RIGHT)
            right_willSink = False
        else:
            right_isSafe = game.boardValueOpen(x+1, y)
            right_willSink = (curSinkCounter == SINK_WARN_TIME - 1 and basicState[3] == 0.5)     
    move_Right = 1*(right_exists and right_isSafe and not right_willSink and not in_bottom_row)
    # current safe
    stay_exists = game.boardValueOpen(x, y)
    if stay_exists:
        if curType != "RIVER":
            stay_isSafe = (curDir == DIR_LEFT and game.boardValueOpen(x+1, y)) or (curDir == DIR_RIGHT and game.boardValueOpen(x-1, y))
            stay_willSink = False
        else:
            stay_isSafe = (curDir == DIR_LEFT and left_exists) or (curDir == DIR_RIGHT and right_exists)
            stay_willSink = (curSinkCounter == SINK_WARN_TIME - 1 and basicState[4] == 0.5)     
    move_Stay = 1*(stay_exists and stay_isSafe and not stay_willSink and not in_bottom_row)
    
    advancedState = [move_Forward, move_Backward, move_Left, move_Right, move_Stay]

    featureKey = (tuple(advancedState), action)
    featureValue = 1
    return [(featureKey, featureValue)]
    
# larger feature extractor
def moreInfoFeatureExtractor(state, action):
    basicState = state[0]
    x = state[1]
    y = state[2]
    justDied = state[3]
    game = state[4]

    if(justDied):
        return [(-10, 1)]
    
    retVal = []
    RADIUS = 2
    curType, curDir, curSinkCounter = game.getRowInfoFromPlayerCoords(y)
    #advancedState = []
    for row in range(max(0, y-2), min(game.height, y+2)):
        type, dir, sinkCounter = game.getRowInfoFromPlayerCoords(row)
        state = tuple([row - y] + [type] + [dir] + [1*(sinkCounter == SINK_WARN_TIME - 1)] + game.getRowFromPlayerCoords(row).getValues(x, RADIUS) + [curDir])
        featureKey = (state, action)
        featureValue = 1
        retVal.append((featureKey, featureValue))
        #advancedState = advancedState + game.getRow(row).getValues(x, RADIUS) + [game.getRowDir(row)] + [1*(game.getRowSinkCounter(row) == SINK_WARN_TIME - 1)]
    
    #featureKey = (tuple(advancedState), action)
    #featureValue = 1
    return retVal