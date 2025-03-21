from QuartoGame import QuartoGame
from QuartoMiniMaxSolver import QuartoMiniMaxSolver
from depthSaver import DepthSaver
import time
import math
import multiprocessing

# Parallel Worker
def solveGame(index, dataLoader, solver):
    game = dataLoader.getGame(index)
    game.printGame()
    score, piece, place, moves = solver.miniMax(game, 32, True, False)
    print(f'Solved Game {index}')

    return moves

# Worker dispatcher
if __name__ == '__main__':
    numWorkers = 22
    solutionName = "testDepth7Sol.txt"
    depthTableName = "testDepth7.txt"
    numToSolve = 50

    dataLoader = DepthSaver()
    dataLoader.loadGames(depthTableName)

    solver = QuartoMiniMaxSolver(depth=32)


    startTime = time.time()
    bestTime, worstTime = math.inf, 0

    startIndex = 0
    while startIndex < numToSolve:
        loopTime = time.time()

        # Calc dispatch indices
        numToDispatch = min(numToSolve - startIndex, numWorkers)
        endIndex = startIndex + numToDispatch
        
        # Dispatch workers
        with multiprocessing.Pool(processes=numToDispatch) as pool:
            # Hash/solution index list
            indices = list(range(startIndex, endIndex))
            # Results, array of solutions that remains parallel to indices after sync
            results = pool.starmap(solveGame, [(indices[i], dataLoader, solver) for i in range(len(indices))])
            #Load synchronized solutions
            for i in range(len(indices)):
                dataLoader.setSolution(indices[i], results[i])
        startIndex += numToDispatch

        currTime = time.time() - loopTime
        worstTime = currTime if currTime > worstTime else worstTime
        bestTime  = currTime if currTime < bestTime else bestTime

    print(f'Took a total of {time.time() - startTime :.03f} seconds')
    print(f'Best Time: {bestTime:.03f} and worst time: {worstTime:.03f}')

    dataLoader.saveSolution(solutionName)


