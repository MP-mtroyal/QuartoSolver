
from QuartoGame import QuartoGame
from QuartoAI import QuartoAI
from QuartoMiniMaxSolver import QuartoMiniMaxSolver
from QuartoIterativeMiniMax import QuartoIterativeMiniMax

import time

if __name__ == "__main__":
    gamesToTest = 1
    currGame = 1
    piecesToStart = 4
    durations = []

    #===== Simple AI playing against itself. 
    # Just a sanity check for seeing that everything is working.
    quit = False
    twistCount = 1

    while not quit:
        print(f'----------------  Game:{currGame} --------------------')
        startTime = time.time()
        g = QuartoGame(twistCount=twistCount)
        g.populateBoard(piecesToStart)
        ai = QuartoMiniMaxSolver(depth=32)
        #ai = QuartoIterativeMiniMax(depth=32, maxBredth=5000)

        #ai.populateCannontableParallel(g, 6)

        
        ai.choosePiece(g)
        timeElapsed = time.time() - startTime
        print(f'Found piece in {timeElapsed:.03f} seconds.')
        durations.append(timeElapsed)
        startTime = time.time()

        # ai.placePiece(g)
        # timeElapsed = time.time() - startTime
        # print(f'Found move in {timeElapsed:.03f} seconds.')
        # durations[-1] += timeElapsed

        
        if currGame >= gamesToTest:
            break
        currGame += 1

    print(f'Average Duration: {sum(durations) / gamesToTest:.03f}')
