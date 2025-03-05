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
        score, _, square = self.miniMax(game, self.depth, True, True)
        if square is not None:
            game.placePiece(game.selectedPieces[0], square)
        else:
            print("Square WAS NONE: You shouldn't see this")

    def choosePiece(self, game: QuartoGame) -> None:
        score, piece, _ = self.miniMax(game, self.depth, True, False)
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
            return self.eval(game, turn), None, None
        cannonGame = self.cannonizer.cannonizeGame(game)
        gameHash = cannonGame.hashBoard()
        

        if placingPiece:
            fullHash = (gameHash, None)
            if fullHash in self.memoTable:
                return self.memoTable[fullHash]
            #try all selected pieces in all avaliable squares
            if len(game.selectedPieces) == 0:
                print("ERROR: NO SELECTED PIECES to be placed")
                return

            bestSquare, bestScore = None, -math.inf

            currPiece = game.selectedPieces[0]
            for square in game.getAvaliableSquares():
                nextGame = game.copy()
                nextGame.placePiece(currPiece, square)
                score, _, _ = self.miniMax(nextGame, depth-1, turn, False)
                if not turn:
                    score *= -1

                if score > bestScore:
                    bestScore = score
                    bestSquare = square
            self.memoTable[(gameHash, currPiece)] = [bestScore, currPiece, bestSquare]
            return [bestScore, None, bestSquare]

        else: #choose piece
            #try selecting all avaliable pieces
            bestPiece, bestScore = None, -math.inf

            for piece in game.getRemainingPieces():
                pieceHash = (gameHash, piece)
                if pieceHash in self.memoTable:
                    return self.memoTable[pieceHash]

                nextGame = game.copy()
                nextGame.selectPiece(piece)

                score, _, _ = self.miniMax(nextGame, depth-1, not turn, True)
                if turn:
                    score *= -1

                if score > bestScore:
                    bestScore = score
                    bestPiece = piece
            if gameHash in self.memoTable:
                self.memoTable[fullHash][1] = bestPiece
            return bestScore, bestPiece, None

    def eval(self, game: QuartoGame, turn: bool):
        if game.checkWin():
            return 1 if turn else -1
        return 0
