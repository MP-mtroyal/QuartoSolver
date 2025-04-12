from Affine4Game import Affine4Game
from AglCannon import AglCannon
from QuartoDataTypes import *
from depthSaver import DepthSaver
from InfoPlotting import LoadingBar
import multiprocessing



def getMoveString(_piece:int, _square: IntVector2):
    return chr(_piece + 64) + chr((_square.x << 2) + _square.y + 64)

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

# ------------------------------------------------------------
# Helper to find the score of a solution string based on whos
# turn it is.
# ------------------------------------------------------------
def find_score(solution: str) -> int:
    if len(solution) % 2 == 0:
        print(f"Invalid score path (even length): {solution}")
        return -999

    if solution[-1] == '1':
        return 0
    if (len(solution) // 2) % 2 == 1:
        return 1
    else:
        return -1

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

def worker(hashes, memoTable):
    #game = Affine4Game(undoMemLength=0)
    solved, unsolved = {}, {}
    for h in hashes:
        if h in memoTable:
            solved[h] = memoTable[h]
        else:
            unsolved[h] = "-"
    return (solved, unsolved)

def solveGame(game:Affine4Game, memoTable, cannonizer:AglCannon, solvedDict, unsolvedDict) -> str:
    pieces = game.getRemainingPieces()
    places = game.getAvaliableSquares()
    triedPieces = set()
    bestScore, bestScorePath = -69, None
    gamehash = game.hashBoard()
    for piece in pieces:
        piece = bestPiece(game, game.getPlacedPieces(), piece)
        if piece in triedPieces:
            continue
        triedPieces.add(piece)
        if not game.selectPiece(piece):
            print("FAILED TO SELECT")
        for place in places:
            if not game.placePiece(piece, place):
                print("FAIL TO PLACE")
            #cannonGame = cannonizer.cannonizeGame(game)
            #cannonHash = cannonGame.hashBoard()
            cannonHash = game.hashBoard()
            if cannonHash not in memoTable:
                print("Failed to find hash in memo table")
                unsolvedDict[gamehash] = "-"
                return False
            score = find_score(memoTable[cannonHash])
            if score > bestScore:
                bestScore = score
                bestScorePath = getMoveString(piece, place) + memoTable[cannonHash]
            if bestScore > 0:
                solvedDict[gamehash] = bestScorePath
                return True

            game.removePiece(place)
        game.deselectAll()
    if bestScorePath is None:
        print("Failed to find score for the following game: ")
        unsolvedDict[gamehash] = "-"
        return False
    solvedDict[gamehash] = bestScorePath
    return True


if __name__ == "__main__":
    srcFolder    = "S:/QuartoStates/AglExplore/"
    memoSrcFile  = "Agl_Level_8_solved_combined.txt"
    unsolvedFile = "Agl_Level_7_to_be_backproped.txt"
    dstFile      = "Agl_Level_7_backproped.txt"
    dstUnsolved  = "Agl_Level_7_backproped_unsolved.txt"

    numWorkers   = 24
    numPerWorker = 100
    currIndex    = 0

    print("Loading Unsolved...")
    # load unsolved
    loader = DepthSaver()
    loader.loadGames(fileName=unsolvedFile, path=srcFolder)
    games = loader.hashes
    loader = None
    print("Loading Solved...")
    # load solutions memo
    loader = DepthSaver()
    loader.loadGames(fileName=memoSrcFile, path=srcFolder)
    solMemo = dict(zip(loader.hashes, loader.solutions))
    loader = None

    print(f"Finding {len(games)} solutions")
    solved, unsolved = {}, {}


    print(f'Solving {len(games)} games')
    game = Affine4Game(undoMemLength=0)
    cannon = AglCannon()
    for i in range(len(games)):
        if i % 10 == 0:
            print(f'Checking game {i}', end='\r')
        game.loadFromHash(games[i])
        solveGame(game, solMemo, cannon, solved, unsolved)

    print(f'Done!!! Solved {len(solved)} games')

    # while currIndex < 10000:
    #     indices, diff = workerListConstructor(games, currIndex, numWorkers, numPerWorker)
    #     with multiprocessing.Pool(processes=len(indices)) as pool:
    #         results = pool.starmap(worker, [(indices[i],solMemo,) for i in range(len(indices))])
    #         for (currSolved, currUnsolved) in results:
    #             for key in currUnsolved.keys():
    #                 if key not in unsolved:
    #                     unsolved[key] = currUnsolved[key]
    #             for key in currSolved.keys():
    #                 if key not in solved:
    #                     solved[key] = currSolved[key]
    #     currIndex += diff
        #print(f'Explored hashes up to {currIndex}, a total of {currIndex / len(games) * 100 :0.3f}%', end="\r")
    #print()

    # for i in range(len(games)):
    #     if i % 10000 == 0:
    #         print(f'Checking game {i}', end='\r')
    #     game = games[i]
    #     if game in solMemo:
    #         solved[game] = solMemo[game]
    #     else:
    #         unsolved[game] = "-"

    print(f'There are {len(solved)} solved games and {len(unsolved)} unsolved games')

    saver = DepthSaver()
    saver.hashes = [key for key in solved.keys()]
    saver.solutions = [solved[key] for key in solved.keys()]
    saver.saveSolution(fileName=dstFile, path=srcFolder)

    saver.hashes = [key for key in unsolved.keys()]
    saver.solutions = [solved[key] for key in unsolved.keys()]
    saver.saveSolution(fileName=dstFile, path=srcFolder)
