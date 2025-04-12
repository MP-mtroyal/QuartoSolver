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

def explorer(games: list[Affine4Game], startDepth:int, expDepth:int):
    solved = {}
    unsolved = set()

    for game in games:

        score, gamePath = solveToDepth(game, False, startDepth, expDepth)

        if '-' in gamePath:
            unsolved.add(game.hashBoard())
        else:
            solved[game.hashBoard()] = gamePath

    return (solved, unsolved)

def solveToDepth(game:Affine4Game, placingPiece:bool, currDepth:int, maxDepth:int):
    if game.checkWinFull():
        return 1, "2"
    if currDepth >= maxDepth:
        return 0, "-"
    bestScore, bestPath = -69, ""
    if placingPiece:
        squares = game.getAvaliableSquares()
        piece   = game.selectedPieces[0]
        bestSquare = None

        for square in squares:
            game.placePiece(piece, square)
            score, gamePath = solveToDepth(game, False, currDepth+1, maxDepth)
            game.removePiece(square)

            if score > bestScore:
                bestScore = score
                bestSquare = square
                bestPath = gamePath
            if bestScore > 0:
                break
        if '-' in bestPath:
            bestPath = '-'
        else:
            squareChr = chr((bestSquare.x << 2) + bestSquare.y + 64)
            bestPath  = squareChr + bestPath
        return bestScore, bestPath

    else:
        pieces = game.getRemainingPieces()
        bestPiece = None
        for piece in pieces:
            game.selectPiece(piece)
            score, gamePath = solveToDepth(game, True, currDepth, maxDepth)
            game.deselectAll()

            if score > bestScore:
                bestScore = score
                bestPath  = gamePath
                bestPiece = piece
            if bestScore > 0:
                break
        if '-' in bestPath:
            bestPath = '-'
        else:
            bestPath = chr(bestPiece + 64) + bestPath
        return -bestScore, bestPath

def exploreHashes(gameHashes:list[int], startDepth:int, expDepth:int):
    games = []
    for gameHash in gameHashes:
        game = Affine4Game(undoMemLength=0)
        game.loadFromHash(gameHash)
        games.append(game)
    results = explorer(games, startDepth, expDepth)
    return results

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


# ==========================================================================================

if __name__ == "__main__":
    #srcFolder = "S:/QuartoStates/AglExplore/"
    srcFolder = "S:/QuartoStates/CPU_Chunks/"

    srcTitles = [
        "Agl_Level_7_unsolved_childless.txt"
        # "CPU_Level_8_chunk3_to_9_unsolved_subChunk5.txt",
        # "CPU_Level_8_chunk3_to_9_unsolved_subChunk6.txt",
        # "CPU_Level_8_chunk3_to_9_unsolved_subChunk7.txt",
        # "CPU_Level_8_chunk3_to_9_unsolved_subChunk8.txt",
        # "CPU_Level_8_chunk3_to_9_unsolved_subChunk9.txt",
        # "CPU_Level_8_chunk3_to_9_unsolved_subChunk10.txt",
        # "CPU_Level_8_chunk3_to_9_unsolved_subChunk5.txt",
        # "CPU_Level_8_chunk3_to_9_unsolved_subChunk6.txt",
        # "CPU_Level_8_chunk3_to_9_unsolved_subChunk7.txt",
        # "CPU_Level_8_chunk3_to_9_unsolved_subChunk8.txt",
        # "CPU_Level_8_chunk3_to_9_unsolved_subChunk9.txt",
        # "CPU_Level_8_chunk3_to_9_unsolved_subChunk10.txt",

        # "CPU_Level_8_chunk4_to_9_unsolved_subChunk1.txt",
        # "CPU_Level_8_chunk4_to_9_unsolved_subChunk2.txt",
        # "CPU_Level_8_chunk4_to_9_unsolved_subChunk3.txt",
        # "CPU_Level_8_chunk4_to_9_unsolved_subChunk4.txt",
        # "CPU_Level_8_chunk4_to_9_unsolved_subChunk5.txt",
        # "CPU_Level_8_chunk4_to_9_unsolved_subChunk6.txt",
        # "CPU_Level_8_chunk4_to_9_unsolved_subChunk7.txt",
        # "CPU_Level_8_chunk4_to_9_unsolved_subChunk8.txt",
        # "CPU_Level_8_chunk4_to_9_unsolved_subChunk9.txt",
        # "CPU_Level_8_chunk4_to_9_unsolved_subChunk10.txt",
    ]
    #srcTitle  = "CPU_Level_8_chunk2_to_9_unsolved_subChunk3.txt"
    #srcTitle  = "Agl_Level_8_unsolved_chunk4.txt"
    dstFolder = "S:/QuartoStates/AglExplore/"
    dstTitles = [
        "CPU_Level_8_chunk_ALL_solved_childless"
        # "CPU_Level_8_chunk3_to_10_subChunk5",
        # "CPU_Level_8_chunk3_to_10_subChunk6",
        # "CPU_Level_8_chunk3_to_10_subChunk7",
        # "CPU_Level_8_chunk3_to_10_subChunk8",
        # "CPU_Level_8_chunk3_to_10_subChunk9",
        # "CPU_Level_8_chunk3_to_10_subChunk10",
        # "CPU_Level_8_chunk3_to_Full_subChunk5",
        # "CPU_Level_8_chunk3_to_Full_subChunk6",
        # "CPU_Level_8_chunk3_to_Full_subChunk7",
        # "CPU_Level_8_chunk3_to_Full_subChunk8",
        # "CPU_Level_8_chunk3_to_Full_subChunk9",
        # "CPU_Level_8_chunk3_to_Full_subChunk10",

        # "CPU_Level_8_chunk4_to_Full_subChunk1",
        # "CPU_Level_8_chunk4_to_Full_subChunk2",
        # "CPU_Level_8_chunk4_to_Full_subChunk3",
        # "CPU_Level_8_chunk4_to_Full_subChunk4",
        # "CPU_Level_8_chunk4_to_Full_subChunk5",
        # "CPU_Level_8_chunk4_to_Full_subChunk6",
        # "CPU_Level_8_chunk4_to_Full_subChunk7",
        # "CPU_Level_8_chunk4_to_Full_subChunk8",
        # "CPU_Level_8_chunk4_to_Full_subChunk9",
        # "CPU_Level_8_chunk4_to_Full_subChunk10",
    ]
    #dstTitle  = "CPU_Level_8_chunk2_to_Full_subChunk3"

    startDepth = 7
    endDepth   = 16

    numWorkers   = 23
    numPerWorkerExplore = 5

    for i in range(len(srcTitles)):
        srcTitle = srcTitles[i]
        dstTitle = dstTitles[i]

        print("=======================================================================")
        print(f"Starting {srcTitle}")

        # Load game hashes only
        games  = []
        loader = DepthSaver()
        loader.loadGames(fileName=srcTitle, path=srcFolder)
        games = []
        for i in range(len(loader.hashes)):
            if loader.solutions[i] is None:
                games.append(loader.hashes[i])
        print(f'Loaded {len(games)} hashes')

        loader = None

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
                results = pool.starmap(exploreHashes, [(indices[i],startDepth, endDepth) for i in range(len(indices))])
                for (currSolved, currUnsolved) in results:
                    for ele in currUnsolved:
                        unsolved.add(ele)
                    for key in currSolved.keys():
                        if key not in solved:
                            solved[key] = currSolved[key]
            currIndex += diff
            print(f'Explored hashes up to {currIndex}, a total of {currIndex / len(games) * 100 :0.3f}%', end="\r")
        print()


        print(f'\n\n{len(solved)} boards were solved and {len(unsolved)} were unsolved.')


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

        if len(unsolved) > 0:
            dummySols = ['-' for _ in range(len(unsolved))]
            saver.hashes = list(unsolved)
            saver.solutions = dummySols
            saver.saveSolution(dstTitle + "_unsolved.txt", path=dstFolder)


