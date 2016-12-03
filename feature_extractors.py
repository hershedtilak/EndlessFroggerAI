from global_vars import *

#test
def testFeatureExtractor(state, action):
    basicState = state[0]
    x = state[1]
    y = state[2]
    justDied = state[3]
    game = state[4]

    if(justDied):
        return [(-10, 1)]

    newState = [1 * (x == 0) for x in basicState[0:4]]
    type, dir, sinkCounter = game.getRowInfoFromPlayerCoords(y-1)
    if type == "RIVER":
        row = game.getRowFromPlayerCoords(game.player.y-1)
        relLogDir = row.getDirOfClosestLog(game.player.x)
        newState.append(relLogDir)
        
    return [((tuple(newState), action), 1)]

# larger feature extractor
def betterThanBaselineFeatureExtractor(state, action):
    basicState = state[0]
    x = state[1]
    y = state[2]
    justDied = state[3]
    game = state[4]

    if(justDied):
        return [(-10, 1)]
    
    retList = []
    advancedState = []
    for row in range(max(0, y-1), min(game.height, y+2)):
        radius = 2 - abs(row - y)
        type, dir, sinkCounter = game.getRowInfoFromPlayerCoords(row)
        advancedState = advancedState + game.getRowFromPlayerCoords(row).getValues(x, radius) + [dir, type, 1*(sinkCounter == SINK_WARN_TIME - 1)]
    
    type, dir, sinkCounter = game.getRowInfoFromPlayerCoords(game.player.y-1)
    if type == "RIVER":
        row = game.getRowFromPlayerCoords(game.player.y-1)
        logDir = row.getDirOfClosestLog(game.player.x)
        advancedState.append(((logDir, action), featureValue))
    
    featureKey = (tuple(advancedState), action)
    featureValue = 1
    retList.append((featureKey, featureValue))
    return retList

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