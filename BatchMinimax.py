from QuartoGame import QuartoGame
from GreatQuartoCannon import GreatQuartoCannon
from QuartoDataTypes import IntVector2
import math

class BatchMinimaxSolver:
    def __init__(self):
        self.memo = {}
        self.numMemoed = 0

    def solveBatch(self, games: list[QuartoGame]) -> list[str]:
        results = []
        for game in games:
            score, sol = self.minimax(game, 0, True, False)
            results.append(sol)

            #game.printGame()
            print(sol)
            #print(f'Memo Table: {len(self.memo)} | Memos Retrieved: {self.numMemoed}')
            #self.printSolution(sol)

        return results

    def printSolution(self, solStr):
        i = 0
        s = ""
        while i < 10000: # dummy stop
            val = ord(solStr[i])
            if val & 64 != 0: # piece place combo
                s += str(val & 15)
                s += "->"

                i += 1
                val = ord(solStr[i])
                x = (val & 12) >> 2
                y = val & 3
                s += "(" + str(x) + "," + str(y) + ")"
                s += "->"

            else: # winning state
                s += "Score:" + str(val - 49)
                break
        
        print(s)


    # Convert value into the valid char range for solutions
    # values should be 0-15, we add 64 because this makes all 16
    # possible chars simple to read, which is nice for parsing
    # if changed, be careful that chars to do include common parse delimeters, 
    # such as commas, new lines, or spaces
    def getValueChar(self, val):
        val = val & 15
        return chr(val + 64)
    
    # Similar to getValueChar, but specificically for final game states
    # must have 0s in the leading half byte (leading nibble?), this works as
    # an end of game delimeter
    def getGameStateChar(self, val):
        return chr(val + 49)

    # Not tracking depth, assumed to be always exploring full depth
    def minimax(self, game: QuartoGame, depth:int, turn: bool, placingPiece: bool):

        # Base Case
        isFinal = game.checkWinFull()
        if isFinal:
            return 1, self.getGameStateChar(1)
        if game.avaliableSquareCount == 0 or game.remainingPieceCount == 0:
            return 0, self.getGameStateChar(0)

        bestScore, bestPiece, bestSquare, bestSol = -math.inf, None, None, None
        gameHash = game.hashBoard()

        if placingPiece:

            piece = game.selectedPieces[0]

            # Check Memoization
            if (gameHash, piece) in self.memo:
                self.numMemoed += 1
                return self.memo[(gameHash, piece)]

            for square in game.getAvaliableSquares():

                if not game.placePiece(piece, square):
                    print("FAILED TO PLACE PIECE")
                
                score, sol = self.minimax(game, depth+1, turn, False)

                game.removePiece(square)

                if score > bestScore:
                    bestScore = score
                    bestSquare = square
                    bestSol = sol

                # Early break if solution was found
                if bestScore > 0:
                    break

            squareIndices = (bestSquare.x << 2) + bestSquare.y
            sol = self.getValueChar(squareIndices) + bestSol
            #sol = [squareIndices] + bestSol

            # Memoize Solution
            self.memo[(gameHash, piece)] = [bestScore, sol]

            return bestScore, sol

        else:

            if (gameHash, None) in self.memo:
                self.numMemoed += 1
                return self.memo[(gameHash, None)]

            score, sol = None, None
            for piece in game.getRemainingPieces():

                if (gameHash, piece) in self.memo:
                    score, sol = self.memo[(gameHash, piece)]

                else:
                    if not game.selectPiece(piece):
                        print("FAILED TO SELECT PIECE")
                    
                    score, sol = self.minimax(game, depth+1, not turn, True)

                    game.deselectAll()

                score *= -1
                
                if score > bestScore:
                    bestScore = score
                    bestPiece = piece
                    bestSol   = sol

                if bestScore > 0:
                    break

            sol = self.getValueChar(bestPiece) + bestSol
            #sol = [bestPiece] + bestSol

            self.memo[(gameHash, None)] = [bestScore, sol]

            return bestScore, sol
