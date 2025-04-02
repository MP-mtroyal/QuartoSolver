
from __future__ import annotations
import numpy as np
from QuartoDataTypes import IntVector2
from QuartoGame import QuartoGame

class Affine4Game(QuartoGame):
    def __init__(self, twistCount=1, verbose=True, undoMemLength=8):
        super().__init__(twistCount, verbose, undoMemLength)

        self.placedPieces = []

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
            if len(line) > 1:
                lines.append(line)
        return lines
    
    def swapPieces(self, index1, index2):
        piece1 = self.board[index1]
        piece2 = self.board[index2]

        self.board[index1] = piece2
        self.board[index2] = piece1

    def getPlacedPieces(self):
        return [self.placedPieces[i] for i in range(len(self.placedPieces))]

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
        g.placedPieces        = self.getPlacedPieces()
        return g

    def placePiece(self, piece, index):
        if super().placePiece(piece, index):
            self.placedPieces.append(piece)
            return True
        exit()
        return False
    
    def removePiece(self, index):
        pieceToRemove = self.board[index]
        if super().removePiece(index) and pieceToRemove >= 0:
            if pieceToRemove in self.placedPieces:
                pieceIndex = self.placedPieces.index(pieceToRemove)
                self.placedPieces = self.placedPieces[:pieceIndex] + self.placedPieces[pieceIndex+1:]
            return True
        exit()
        return False
    
    def selectPiece(self, piece):
        if super().selectPiece(piece):
            return True
        self.printGame()
        print(piece)
        print(self.selectedPieces)
        print(self.getRemainingPieces())
        exit()
        return False
    
    def xorPieces(self, xorPiece):
        if xorPiece > 0:
            super().xorPieces(xorPiece)
            for i in range(len(self.placedPieces)):
                self.placedPieces[i] = self.placedPieces[i] ^ xorPiece


    def sanityCheck_PiecesPlaced(self, shouldPrint=False):
        count = 0
        for y in range(self.board.shape[0]):
            for x in range(self.board.shape[1]):
                if self.board[IntVector2(x,y)] >= 0:
                    count += 1
        if count != len(self.placedPieces):
            if shouldPrint:
                print("Sanity check FAILURE!")
                self.printGame()
            return False

        return True
    
    def loadFromHash(self, boardHash):
        super().loadFromHash(boardHash)
        # Populate order of piece placement in arbitrary order
        for y in range(self.board.shape[0]):
            for x in range(self.board.shape[1]):
                index = IntVector2(x,y)
                if self.board[index] >= 0:
                    self.placedPieces.append(self.board[index])