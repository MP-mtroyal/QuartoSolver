from QuartoGame import QuartoGame
from QuartoDataTypes import IntVector2
from BasicQuartoCannon import BasicQuartoCannon
import math
import random


class MiniMaxSolver:

    def __init__(self, depth=16):
        self.memoTable = {}
        self.depth = depth
        self.cannonizer = BasicQuartoCannon()

    def placePiece(self, game: QuartoGame) -> None:
        score, _, square, moves = self.miniMax(game, self.depth, True, True)
        print("Placement Path: ", end="")
        print(moves)
        print()
        if square is not None:
            game.placePiece(game.selectedPieces[0], square)
        else:
            print("Square WAS NONE: You shouldn't see this")

    def choosePiece(self, game: QuartoGame) -> None:
        score, piece, _, moves = self.miniMax(game, self.depth, True, False)
        print("Placement Path: ", end="")
        print(moves)
        print()
        if piece is not None:
            game.selectPiece(piece)
        else:
            print("PIECE WAS NONE: You shouldn't see this")

    def miniMax(
            self,
            game: QuartoGame,
            depth: int,
            turn: bool, #true if it is the current AI's turn
            placingPiece: bool
    ):
        if depth == 0 or game.checkWin() or len(game.getAvaliableSquares()) == 0 or len(game.getRemainingPieces()) == 0:
            gameState = self.eval(game, turn)
            return gameState, None, None, " Score:" + str(gameState)
        cannonGame = self.cannonizer.cannonizeGame(game)
        gameHash = cannonGame.hashBoard()
        

        if placingPiece:
            #try all selected pieces in all avaliable squares
            if len(game.selectedPieces) == 0:
                print("ERROR: NO SELECTED PIECES to be placed")
                return

            bestMoves, bestSquare, bestScore = None, None, -math.inf
            moves = None
            currPiece = game.selectedPieces[0]
            pieceHash = (gameHash, currPiece)
            if pieceHash in self.memoTable:
                score, move, square, moveStr = self.memoTable[pieceHash]
                if not turn:
                    score *= -1
                return score, move, square, moveStr
            
            for square in game.getAvaliableSquares():
                nextGame = game.copy()

                if not nextGame.placePiece(currPiece, square):
                    print("FAILED TO PLACE")
                score, _, _, moves = self.miniMax(nextGame, depth-1, turn, False)
                if not turn:
                    score *= -1

                if score > bestScore:
                    bestScore = score
                    bestSquare = square
                    bestMoves = moves
            moveStr = f'({bestSquare.x},{bestSquare.y})' + "->" + bestMoves
            self.memoTable[pieceHash] = [bestScore, currPiece, bestSquare, moveStr]
            return bestScore, None, bestSquare, moveStr

        else: #choose piece
            #try selecting all avaliable pieces
            bestMoves, bestPiece, bestScore = None, None, -math.inf
            moves = None

            for piece in game.getRemainingPieces():
                pieceHash = (gameHash, piece)
                if pieceHash in self.memoTable:
                    score, _, _, moves = self.memoTable[pieceHash]
                else:
                    nextGame = game.copy()
                    if not nextGame.selectPiece(piece):
                        print("FAILED TO SELECT")

                    score, _, _, moves = self.miniMax(nextGame, depth-1, not turn, True)
                if turn:
                    score *= -1

                if score > bestScore:
                    bestScore = score
                    bestPiece = piece
                    bestMoves = moves
            moveStr = str(bestPiece) + "->" + bestMoves
            return bestScore, bestPiece, None, moveStr

    def eval(self, game: QuartoGame, turn: bool):
        if game.checkWin():
            return 1 if turn else -1
        return 0
