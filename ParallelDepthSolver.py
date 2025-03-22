from QuartoGame import QuartoGame
from QuartoMiniMaxSolver import QuartoMiniMaxSolver
from depthSaver import DepthSaver
import time
import math
import multiprocessing
from BatchMinimax import BatchMinimaxSolver

# Parallel Worker
def solveGame(index, dataLoader, solver):
    game = dataLoader.getGame(index)
    game.printGame()
    score, piece, place, moves = solver.miniMax(game, 32, True, False)
    print(f'Solved Game {index}')

    return moves

def solveGameBatch(indices, dataLoader):
    solver = BatchMinimaxSolver()
    games = [dataLoader.getGame(indices[i]) for i in range(len(indices))]
    solutions = solver.solveBatch(games)
    return solutions

# Worker dispatcher
if __name__ == '__main__':
    numWorkers = 5
    solutionName = "testDepth7Sol.txt"
    depthTableName = "testDepth7.txt"
    numToSolve = 50
    numPerBatch = 5

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
        
        # ================= batch testing!! ==================

        batchSolver = BatchMinimaxSolver()

        games = [dataLoader.getGame(i) for i in range(10)]

        #batchSolver.solveBatch(games)

        #with multiprocessing.Pool(processes=numToDispatch) as pool:
        indices = []
        index = startIndex
        for i in range(numWorkers):
            workerIndices = []
            for n in range(numPerBatch):
                workerIndices.append(index)
                index += 1
                if index >= numToSolve:
                    break
            indices.append(workerIndices)
            if index >= numToSolve:
                break
        
        with multiprocessing.Pool(processes=len(indices)) as pool:
            print(indices)
            results = pool.starmap(solveGameBatch, [(indices[i], dataLoader) for i in range(len(indices))])
            for i in range(len(results)):
                for n in range(len(results[i])):
                    dataLoader.setSolution(indices[i][n], results[i][n])

        startIndex += numWorkers * numPerBatch

        currTime = time.time() - loopTime
        worstTime = currTime if currTime > worstTime else worstTime
        bestTime  = currTime if currTime < bestTime else bestTime

    print(f'Took a total of {time.time() - startTime :.03f} seconds')
    print(f'Best Time: {bestTime:.03f} and worst time: {worstTime:.03f}')

    dataLoader.saveSolution(solutionName)


