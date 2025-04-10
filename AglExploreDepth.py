# Explores one depth level of an AGL board

from Affine4Game import Affine4Game
from AglCannon import AglCannon
from QuartoDataTypes import *
from depthSaver import DepthSaver
from InfoPlotting import LoadingBar
import multiprocessing


def getSolutionString(_piece:int, _square: IntVector2, _score:int):
    return chr(_piece + 64) + chr((_square.x << 2) + _square.y + 64) + chr(_score + 49)


# ==================== Best piece selection functions =======================================
def traitsInCommon(p1, p2):
    commonTraits =  bin(p1 & p2).count('1')
    commonTraits += bin((p1 ^ 15) & (p2 ^ 15)).count('1')
    return commonTraits

# Finds best piece that could be placed which is invariant to 'toPlace' if the current
# pieces on the board are 'placed'

def bestPiece(game: Affine4Game, placed: list[int], toPlace:int):
    for i in range(toPlace):
        if game.remainingPieces[i] < 1:
            continue
        for n in range(len(placed)):
            # End loop early if current pieces shares a different number of traits
            # in common with the placed piece
            if traitsInCommon(i, placed[n]) != traitsInCommon(toPlace, placed[n]):
                break
        # If the loop didn't end early, return the current piece
        else:
            return i
    return toPlace
# ==========================================================================================


# ============= Parallel Exploration =======================================================

def explorer(games):
    solved = {}
    unsolved = set()

    for game in games:
        pieces = game.getRemainingPieces()
        places = game.getAvaliableSquares()
        found = False
        currUnsolved = []
        parentHash = game.hashBoard()
        #triedPieces = set()
        for piece in pieces:
            # piece = bestPiece(game, game.getPlacedPieces(), piece)
            # if piece in triedPieces:
            #     continue
            # triedPieces.add(piece)
            
            if not game.selectPiece(piece):
                print("FAILED TO SELECT PIECE")
                exit()
            for square in places:
                if not game.placePiece(piece, square):
                    print("FAILED TO PLACE PIECE")
                    exit()
                if not game.checkWinFull():
                    currUnsolved.append(game.hashBoard())
                else:
                    if parentHash not in solved:
                        solved[parentHash] = getSolutionString(piece, square, 1)
                    found = True
                    break

                game.removePiece(square)
            game.deselectAll()
            if found:
                break

        if not found:
            for i in range(len(currUnsolved)):
                unsolved.add(currUnsolved[i])

    return (solved, unsolved)

def exploreHashes(gameHashes):
    games = []
    for gameHash in gameHashes:
        game = Affine4Game(undoMemLength=0)
        game.loadFromHash(gameHash)
        games.append(game)
    results = explorer(games)
    return results

# ==========================================================================================

# ============= Parallel cannonization =====================================================
def workerListConstructor(values, startIndex, numWorkers, numPerWorker):
    results = []
    index = startIndex
    for i in range(numWorkers):
        workerValues = []
        for n in range(numPerWorker):
            if index >= len(values):
                if len(workerValues) > 0:
                    results.append(workerValues)
                return results, index - startIndex
            workerValues.append(values[index])
            index += 1
        results.append(workerValues)
    return results, index - startIndex

def cannonSolver(gameHashes:list[int], cannonizer:AglCannon):
    cannonHashes = []
    game = Affine4Game()
    for gameHash in gameHashes:
        game.loadFromHash(gameHash)
        cannonGame = cannonizer.cannonizeGame(game)
        cannonHashes.append(cannonGame.hashBoard())
    return cannonHashes

# ==========================================================================================

if __name__ == "__main__":
    srcFolder = "S:/QuartoStates/AglExplore/"
    srcTitle  = "Agl_Level_3_unsolved.txt"
    dstFolder = "S:/QuartoStates/AglExplore/"
    dstTitle  = "Agl_Level_4_fullTest"

    numWorkers   = 24
    numPerWorkerExplore = 1000
    numPerWorkerCannon = 1000

    # Load games
    # games  = []
    # loader = DepthSaver()
    # loader.loadGames(fileName=srcTitle, path=srcFolder)
    # loadingBar = LoadingBar(len(loader.hashes), title="Loading Games", interval=1000)
    # for i in range(len(loader.hashes)):
    #     loadingBar.update()
    #     games.append(loader.getGame(i, isAffine=True))
    # loadingBar.complete()

    # Load game hashes only
    games  = []
    loader = DepthSaver()
    loader.loadGames(fileName=srcTitle, path=srcFolder)
    games = loader.hashes

    if len(games) == 0:
        print("Failed to load games")
        exit()

    # Find next level games
    solved = {}
    unsolved = set()
    currIndex = 0

    while currIndex < len(games):
        indices, diff = workerListConstructor(games, currIndex, numWorkers, numPerWorkerExplore)
        with multiprocessing.Pool(processes=len(indices)) as pool:
            #results = pool.starmap(explorer, [(indices[i],) for i in range(len(indices))])
            results = pool.starmap(exploreHashes, [(indices[i],) for i in range(len(indices))])
            for (currSolved, currUnsolved) in results:
                for ele in currUnsolved:
                    unsolved.add(ele)
                for key in currSolved.keys():
                    if key not in solved:
                        solved[key] = currSolved[key]
        currIndex += diff
        print(f'Explored hashes up to {currIndex}, a total of {currIndex / len(games) * 100 :0.3f}%', end="\r")
    print()

    # gameIndex = 1
    # updateInterval = 10
    # totalGames = len(games)
    # print("Exploring Games...")
    # for game in games:
    #     if gameIndex % updateInterval == 0:
    #         print(f'Exploring game {gameIndex} of {totalGames}, {gameIndex / totalGames * 100 :0.3f}% complete.', end="\r")
    #     gameIndex += 1

    #     pieces = game.getRemainingPieces()
    #     places = game.getAvaliableSquares()
    #     found = False
    #     currUnsolved = []
    #     parentHash = game.hashBoard()
    #     triedPieces = set()
    #     for piece in pieces:
    #         piece = bestPiece(game, game.getPlacedPieces(), piece)
    #         if piece in triedPieces:
    #             continue
    #         triedPieces.add(piece)
            
    #         if not game.selectPiece(piece):
    #             print("FAILED TO SELECT PIECE")
    #             exit()
    #         for square in places:
    #             if not game.placePiece(piece, square):
    #                 print("FAILED TO PLACE PIECE")
    #                 exit()
    #             if not game.checkWinFull():
    #                 currUnsolved.append(game.hashBoard())
    #             else:
    #                 if parentHash not in solved:
    #                     solved[parentHash] = getSolutionString(piece, square, 1)
    #                 found = True
    #                 break

    #             game.removePiece(square)
    #         game.deselectAll()
    #         if found:
    #             break

    #     if not found:
    #         for i in range(len(currUnsolved)):
    #             unsolved.add(currUnsolved[i])

    print(f'\n\n{len(solved)} boards were solved and {len(unsolved)} were unsolved.')


# ------------------------ Cannonizing -----------------------------
    # game         = Affine4Game(undoMemLength=0)
    # cannon       = AglCannon()
    # cannonHashes = set()
    # unsolved     = list(unsolved)
    # currIndex    = 0

    # while currIndex < len(unsolved):
    #     indices, diff = workerListConstructor(unsolved, currIndex, numWorkers, numPerWorkerCannon)
    #     with multiprocessing.Pool(processes=len(indices)) as pool:
    #         results = pool.starmap(cannonSolver, [(indices[i], cannon) for i in range(len(indices))])
    #         for result in results:
    #             for ele in result:
    #                 cannonHashes.add(ele)
    #     currIndex += diff
    #     print(f'Found cannon hashes up to {currIndex}, a total of {currIndex / len(unsolved) * 100 :0.3f}%', end="\r")
    # print()

    # Removed cannonizing at 7 piece placed
    cannonHashes = unsolved


    print(f'Found {len(unsolved)} new boards which cannonize to {len(cannonHashes)} boards.')

    # ------------------------ Save Results --------------------------------------
    saver = DepthSaver()
    hashes, sols = [], []

    if len(solved) > 0:
        for key in solved.keys():
            sols.append(solved[key])
            hashes.append(key)
        saver.hashes = hashes
        saver.solutions = sols
        saver.saveSolution(dstTitle + "_solved.txt", path=dstFolder)

    if len(cannonHashes) > 0:
        dummySols = ['-' for _ in range(len(cannonHashes))]
        saver.hashes = list(cannonHashes)
        saver.solutions = dummySols
        saver.saveSolution(dstTitle + "_unsolved.txt", path=dstFolder)


    # for game in games:
    #     pieces = game.getRemainingPieces()
    #     places = game.getAvaliableSquares()
    #     for piece in pieces:
    #         piece = bestPiece(game, game.getPlacedPieces(), piece)
    #         if piece in triedPieces:
    #             continue
            
    #         if not game.selectPiece(piece):
    #             print("FAILED TO SELECT PIECE")
    #             exit()
    #         for square in places:
    #             if not game.placePiece(piece, square):
    #                 print("FAILED TO PLACE PIECE")
    #                 exit()
    #             if not game.checkWinFull():
    #                 unsolved.add(game.hashBoard())
    #             else:
    #                 gameHash = game.hashBoard()
    #                 if gameHash not in solved:
    #                     solved[gameHash] = getSolutionString(piece, square, 1)

    #             game.removePiece(square)
    #         game.deselectAll()