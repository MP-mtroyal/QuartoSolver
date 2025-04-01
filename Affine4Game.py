
from __future__ import annotations
import numpy as np
from QuartoDataTypes import IntVector2
from QuartoGame import QuartoGame

class Affine4Game(QuartoGame):
    def __init__(self, twistCount=1, verbose=True, undoMemLength=8):
        super().__init__(twistCount, verbose, undoMemLength)

        self.lineIndexLists = [
            # Horizontals 
            [IntVector2(0,0), IntVector2(1,0), IntVector2(2,0), IntVector2(3,0)],
            [IntVector2(0,1), IntVector2(1,1), IntVector2(2,1), IntVector2(3,1)],
            [IntVector2(0,2), IntVector2(1,2), IntVector2(2,2), IntVector2(3,2)],
            [IntVector2(0,3), IntVector2(1,3), IntVector2(2,3), IntVector2(3,3)],
            # Verticals
            [IntVector2(0,0), IntVector2(0,1), IntVector2(0,2), IntVector2(0,3)],
            [IntVector2(1,0), IntVector2(1,1), IntVector2(1,2), IntVector2(1,3)],
            [IntVector2(2,0), IntVector2(2,1), IntVector2(2,2), IntVector2(2,3)],
            [IntVector2(3,0), IntVector2(3,1), IntVector2(3,2), IntVector2(3,3)],
            # Diagonals
            [IntVector2(0,0), IntVector2(1,1), IntVector2(2,2), IntVector2(3,3)],
            [IntVector2(0,3), IntVector2(1,2), IntVector2(2,1), IntVector2(3,0)],

            [IntVector2(0,0), IntVector2(2,1), IntVector2(3,2), IntVector2(1,3)],
            [IntVector2(0,0), IntVector2(3,1), IntVector2(1,2), IntVector2(2,3)],

            [IntVector2(1,0), IntVector2(0,1), IntVector2(3,2), IntVector2(2,3)],
            [IntVector2(1,0), IntVector2(2,1), IntVector2(0,2), IntVector2(3,3)],
            [IntVector2(1,0), IntVector2(3,1), IntVector2(2,2), IntVector2(0,3)],

            [IntVector2(2,0), IntVector2(1,1), IntVector2(3,2), IntVector2(0,3)],
            [IntVector2(2,0), IntVector2(0,1), IntVector2(1,2), IntVector2(3,3)],
            [IntVector2(2,0), IntVector2(3,1), IntVector2(0,2), IntVector2(1,3)],

            [IntVector2(3,0), IntVector2(0,1), IntVector2(2,2), IntVector2(1,3)],
            [IntVector2(3,0), IntVector2(1,1), IntVector2(0,2), IntVector2(2,3)],
        ]

    def updateWinStatus(self, index):
        print(f'Update Win Status for Affine plane not implemented')
        return 
    
    def getPiecesInIndices(self, indices):
        pieces = []
        for index in indices:
            pieces.append(self.board[index])
        return pieces
    
    def getCommonLines(self):
        lines = []
        for indices in self.lineIndexLists:
            line = []
            for index in indices:
                if self.board[index] >= 0:
                    line.append(self.board[index])
            if len(line) > 0:
                lines.append(line)
        return lines

    def getPlacedPieces(self):
        pieces = []
        for y in range(self.board.shape[0]):
            for x in range(self.board.shape[1]):
                index = IntVector2(x,y)
                if self.board[index] >= 0:
                    pieces.append(self.board[index])
        return pieces

    # Short circuit check win not implemented
    def checkWin(self):
        return self.checkWinFull()

    def checkWinFull(self):
        for indices in self.lineIndexLists:
            if self.checkFeatureList(self.getPiecesInIndices(indices)):
                return True
        return False
    

    def copy(self, dest:Affine4Game=None) -> Affine4Game:
        g                 = dest if dest is not None else Affine4Game(self.twistCount, self.verbose)
        g.dims            = IntVector2(self.dims.x, self.dims.y)
        g.selectedPieces  = [piece for piece in self.selectedPieces]
        g.board           = np.copy(self.board)
        g.remainingPieces = np.copy(self.remainingPieces)
        g.undoMemLength   = self.undoMemLength
        g.isWinningState  = self.isWinningState
        g.avaliableSquareCount = self.avaliableSquareCount
        g.remainingPieceCount = self.remainingPieceCount
        g.selectedPieceCount  = self.selectedPieceCount
        return g
