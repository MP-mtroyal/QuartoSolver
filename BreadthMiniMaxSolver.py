from QuartoGame import QuartoGame
from Affine4Game import Affine4Game
import math
from QuartoDataTypes import IntVector2
from depthSaver import DepthSaver

NOT_EXPLORED_FLAG = -69

class BreadthMiniMaxSolver:

    def __init__(self):
        self.memoTable      = {}
        self.solvedGames    = {}
        self.unsolvedGames  = {}
        self.depthToExplore = 0

    def exploreBatch(self, games: list[QuartoGame], startDepth: int, endDepth: int):
        self.solvedGames    = {}
        self.unsolvedGames  = {}
        self.depthToExplore = endDepth
        index = 0
        for game in games:
            index += 1
            if index % 100 == 0:
                print(f'{(index / len(games)) * 100 :.03f}%', end='\r')
            score, solution = self.miniMax(game, startDepth, False)
            if score == NOT_EXPLORED_FLAG:
                self.unsolvedGames[game.hashBoard()] = '-'
            else:
                self.solvedGames[game.hashBoard()] = solution

    def miniMax(
            self, 
            game:QuartoGame, 
            depth:int, 
            placingPiece: bool
    ):
        if game.checkWinFull():
            return 1, chr(49 + 1)
        
        if game.avaliableSquareCount <= 0 or game.remainingPieceCount <= 0:
            return 0, chr(49)

        if depth > self.depthToExplore:
            return NOT_EXPLORED_FLAG, "-"

        gameHash = game.hashBoard()

        bestScore, bestMoves, bestSquare, bestPiece = -math.inf, "", None, None
        notFullyExplored = False

        if placingPiece:
            # Get current piece
            piece = game.selectedPieces[0]
            # Check Memo Table for solution
            pieceHash = (gameHash, piece)
            if pieceHash in self.memoTable:
                return self.memoTable[pieceHash]
            # Explore the avaliable squares
            for square in game.getAvaliableSquares():
                if not game.placePiece(piece, square):
                    print("FAILED TO PLACE PIECE")
                score, moves = self.miniMax(game, depth+1, False)
                game.removePiece(square)

                if score == -69: # Not explored flag
                    notFullyExplored = True
                elif score > bestScore:
                    bestScore  = score
                    bestMoves  = moves
                    bestSquare = square
                # Minimax early eval
                if bestScore > 0: 
                    notFullyExplored = False # early eval doesn't care if others explored
                    break
            
            if notFullyExplored:
                bestScore = NOT_EXPLORED_FLAG
                moveStr = "-" + bestMoves
            else:
                bestSquareVal = (bestSquare.x << 2) + bestSquare.y
                moveStr = chr(bestSquareVal + 64) + bestMoves

            self.memoTable[pieceHash] = (bestScore, moveStr)

            return (bestScore, moveStr)

        else:
            # Check Memo Table for solution
            pieceHash = (gameHash, None)
            if pieceHash in self.memoTable:
                return self.memoTable[pieceHash]

            for piece in game.getRemainingPieces():
                
                if not game.selectPiece(piece):
                    print("FAILED TO SELECT")
                score, moves = self.miniMax(game, depth, True)
                game.deselectAll()

                if score == NOT_EXPLORED_FLAG:
                    notFullyExplored = True
                elif score > bestScore:
                    bestScore = score
                    bestMoves = moves
                    bestPiece = piece

                if bestScore > 0:
                    break

            if notFullyExplored:
                bestScore = NOT_EXPLORED_FLAG
                moveStr = "-" + bestMoves
            else:
                bestScore *= -1
                moveStr = chr(bestPiece + 64) + bestMoves

            self.memoTable[pieceHash] = (bestScore, moveStr)

            return (bestScore, moveStr)


saver = DepthSaver(cannon=None)
saver.loadGames("Affine6BoardsSmall.txt", "S:/QuartoStates/")
print("  ---   Games Loaded   ---   ")
allGames = []
solver = BreadthMiniMaxSolver()

for gameHash in saver.hashes:
    currGame = Affine4Game()
    currGame.loadFromHash(gameHash)
    allGames.append(currGame)

print("  ---   Games Built   ---   ")

solver.exploreBatch(allGames, 6, 7)

print()
print(f'\nFound {len(solver.solvedGames.keys())} solutions and {len(solver.unsolvedGames.keys())} unsolved.\n')

sols, hashes = [], []

for key in solver.solvedGames.keys():
    sols.append(solver.solvedGames[key])
    hashes.append(key)

saver.solutions = sols
saver.hashes = hashes

saver.saveSolution("Affine6BoardsSmall_Solved_Depth7.txt")

sols, hashes = [], []

for key in solver.unsolvedGames.keys():
    sols.append(solver.unsolvedGames[key])
    hashes.append(key)

saver.solutions = sols
saver.hashes = hashes

saver.saveSolution("Affine6BoardsSmall_Unsolved_Depth7.txt")
