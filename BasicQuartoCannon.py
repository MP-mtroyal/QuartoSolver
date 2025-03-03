from QuartoGame import QuartoGame
from QuartoCannon import QuartoCannon
from QuartoDataTypes import IntVector2
import numpy as np

class BasicQuartoCannon(QuartoCannon):
    def __init__(self):
        super().__init__()

    def flipForScoreAllMasks(self, board, splitFunc, flipFunc):
        masks = [15] + [2 ** i for i in range(4)]
        for mask in masks:
            newBoard = self.flipForScore(board, mask, splitFunc, flipFunc)
            if newBoard != None:
                return newBoard
        # All masks resulted in ties
        return board

    def flipForScore(self, board, mask, splitFunc, flipFunc):
        a, b = splitFunc(board)
        aScore = self.scoreList(a, mask)
        bScore = self.scoreList(b, mask)
        if aScore == bScore:
            return None #Indeterminant
        if aScore < bScore:
            board = flipFunc(board)
        return board

    def scoreList(self, featList, mask):
        result = []
        for feat in featList:
            result += feat & mask
        return result

    def diagonalSplit(self, board):
        topRight, bottomLeft = [], []
        for y in range(len(board)):
            for x in range(len(board[0])):
                index = IntVector2(x,y)
                if x < y:
                    bottomLeft.append(board[index])
                elif y < x:
                    topRight.append(board[index])
        return bottomLeft, topRight

    def horizontalSplit(self, board):
        board = board.transpose()
        up, down = self.verticalSplit(board)
        return up, down

    def verticalSplit(self, board):
        left, right = [], []
        for y in range(len(board)):
            for x in range(len(board[0])):
                index = IntVector2(x,y)
                if x < len(board) // 2:
                    left.append(board[index])
                else:
                    right.append(board[index])
        return left, right

    def diagonalReflect(self, board):
        return board.transpose()

    def horizontalReflect(self, board):
        board = board.transpose()
        board = self.verticalReflect(board)
        board = board.transpose()
        return board

    def verticalReflect(self, board):
        for i in range(len(board) // 2):
            temp = board[i]
            board[i] = board[-(i+1)]
            board[-(i+1)] = temp
        return board

    def cannonizeGame(self, game):
        game  = game.copy()
        board = game.board
        board = self.flipForScoreAllMasks(board, self.horizontalSplit, self.horizontalReflect)
        board = self.flipForScoreAllMasks(board, self.verticalSplit, self.verticalReflect)
        board = self.flipForScoreAllMasks(board, self.diagonalSplit, self.diagonalReflect)
        game.board = board
        return game
    
    def reset(self):
        return super().reset()
    
