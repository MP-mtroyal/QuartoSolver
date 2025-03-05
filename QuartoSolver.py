
from QuartoGame import QuartoGame
from QuartoAI import QuartoAI
from MiniMaxAI import MiniMaxAI
from MiniMaxAI2 import MiniMaxSolver

import time

gamesToTest = 1
currGame = 1
piecesToStart = 6
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
    ai = MiniMaxSolver(depth=6)

    
    ai.choosePiece(g)
    timeElapsed = time.time() - startTime
    print(f'Found piece in {timeElapsed:.03f} seconds.')
    durations.append(timeElapsed)
    startTime = time.time()

    # while not g.checkWin() and len(g.getRemainingPieces()) > 0 and len(g.getAvaliableSquares()) > 0:
    #     for _ in range(twistCount):
    #         if len(g.getRemainingPieces()) < 1:
    #             break
    #         ai.choosePiece(g)
    #     ai.placePiece(g)
    
    ai.placePiece(g)
    timeElapsed = time.time() - startTime
    print(f'Found move in {timeElapsed:.03f} seconds.')
    durations[-1] += timeElapsed


    #if g.checkWin():
    #    print('WINNER!')
    #else:
        #print("Stalemate :(")
    
    if currGame >= gamesToTest:
        break
    currGame += 1

print(f'Average Duration: {sum(durations) / gamesToTest:.03f}')

    #c = input('\nPlay again? y/n  ')
    #if c != 'y':
    #    quit = True