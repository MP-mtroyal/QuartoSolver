
from QuartoGame import QuartoGame
from QuartoAI import QuartoAI
from QuartoMiniMaxSolver import QuartoMiniMaxSolver

import time

gamesToTest = 1
currGame = 1
piecesToStart = 0
durations = []

#===== Simple AI playing against itself. 
# Just a sanity check for seeing that everything is working.
quit = False
twistCount = 1

print(time.process_time_ns())

while not quit:
    print(f'----------------  Game:{currGame} --------------------')
    startTime = time.time()
    g = QuartoGame(twistCount=twistCount)
    g.populateBoard(piecesToStart)
    ai = QuartoMiniMaxSolver(depth=9)

    
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
