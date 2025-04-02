from Affine4Cannon import Affine4Cannon
from Affine4Game import Affine4Game
from depthSaver import DepthSaver
import time
import math
import multiprocessing

def worker(indices, dataloader:DepthSaver):
    cannon = Affine4Cannon()
    solutions = set()
    games = [dataloader.getGame(index, isAffine=True) for index in indices]
    for game in games:
        #game = dataloader.getGame(index, isAffine=True)
        pieces = game.getRemainingPieces()
        places = game.getAvaliableSquares()
        for piece in pieces:
            game.selectPiece(piece)
            for square in places:
                game.placePiece(piece, square)
                #cannonGame = cannon.cannonizeGame(game)
                solutions.add(game.hashBoard())
                game.removePiece(square)
            game.deselectAll()
    return list(solutions)


if __name__ == "__main__":
    numWorkers = 22
    srcTable   = "Affine7Chunk_1.txt"
    dstTable   = "Affine8Chunk_1.txt"
    depthTableLocation = "S:/QuartoStates/"

    solutions = set()

    numToSolve = 1_000_000
    numPerBatch = 5000

    dataLoader = DepthSaver(cannon=None)
    dataLoader.loadGames(fileName=srcTable, path=depthTableLocation)

    numToSolve = min(numToSolve, len(dataLoader.hashes))

    startTime = time.time()
    bestTime, worstTime = math.inf, 0

    startIndex = 0
    while startIndex < numToSolve:
        loopTime = time.time()

        numToDispatch = min(numToSolve - startIndex, numWorkers)
        endIndex      = startIndex + numToDispatch

        print(f' ============ Creating indices starting at {startIndex} =============== ')
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
            results = pool.starmap(worker, [(indices[i], dataLoader) for i in range(len(indices))])
            for result in results:
                for ele in result:
                    solutions.add(ele)

        startIndex += numWorkers * numPerBatch
        currTime = time.time() - loopTime
        worstTime = currTime if currTime > worstTime else worstTime
        bestTime  = currTime if currTime < bestTime else bestTime
    
    print("Complete!")
    print(f'Took a total of {time.time() - startTime :.03f} seconds')
    print(f'Best Time: {bestTime:.03f} and worst time: {worstTime:.03f}')
    print(f"Solutions: {len(solutions)}")

    dataLoader.hashes = list(solutions)
    dataLoader.saveSolution(dstTable, depthTableLocation)