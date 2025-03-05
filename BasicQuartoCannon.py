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
            if newBoard is not None:
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
        result = -1
        for feat in featList:
            feat = int(feat)
            if feat >= 0:
                if result < 0 : result = 0
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

    def verticalSplit(self, board):
        board = board.transpose()
        up, down = self.horizontalSplit(board)
        return up, down

    def horizontalSplit(self, board):
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

    def verticalReflect(self, board):
        board = np.flip(board, axis=1)
        return board

    def horizontalReflect(self, board):
        board = np.flip(board, axis=0)
        return board
    
    def xorMatrix(self, board):
        xorValue = -1
        for y in range(board.shape[0]):
            for x in range(board.shape[1]):
                index = IntVector2(x,y)
                if xorValue < 0 and board[index] >= 0:
                    xorValue = int(board[index])
                if board[index] >= 0:
                    board[index] = int(board[index]) ^ xorValue
        return board

    def cannonizeGame(self, game):
        if sum(sum(game.board)) < -15:
            return game
        # print(" = = = = = = = = = = = = = = = =  = = = = = = = = = = ")
        # game.printGame()
        game  = game.copy()
        board = game.board
        board = self.flipForScoreAllMasks(board, self.horizontalSplit, self.horizontalReflect)
        board = self.flipForScoreAllMasks(board, self.verticalSplit, self.verticalReflect)
        board = self.flipForScoreAllMasks(board, self.diagonalSplit, self.diagonalReflect)

        #board = self.xorMatrix(board)
        game.board = board
        # print()
        # game.printGame()
        return game
    
    def reset(self):
        return super().reset()
    

