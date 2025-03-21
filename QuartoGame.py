from __future__ import annotations

import numpy as np
import math
from QuartoDataTypes import IntVector2
import random

import FastCannon

random.seed(3)

class QuartoGame:
    def __init__(self, twistCount=1, verbose=True, undoMemLength=8):
        self.twistCount      = twistCount
        self.verbose         = verbose
        self.dims            = IntVector2(4, 4) #hardcoded to 4x4 for now
        #self.selectedPieces  = np.array([], dtype=np.int32)
        self.selectedPieces = []
        self.board           = - np.ones(self.dims, dtype=np.int16, order='C')
        #self.remainingPieces = [1 for i in range(self.dims[0] * self.dims[1])]
        self.remainingPieces = np.ones([self.dims[0] * self.dims[1]],dtype=np.uint8)

        self.selectedPieceCount  = 0
        self.avaliableSquareCount = self.dims[0] * self.dims[1]
        self.remainingPieceCount = self.dims[0] * self.dims[1]

        self.undoMemLength  = undoMemLength
        self.undoStack      = []
        self.isWinningState = False
        self.last_move = None

#======= Copies data of this game, and returns a copy ==========
#   dest (QuartoGame): If dst is specified, data is copied into this the 
#                   dest QuartoGame. Otherwise, a new QuartoGame is created
#   Copied games are NEW games, and therefore do not have an undo stack loaded
    def copy(self, dest:QuartoGame=None) -> QuartoGame:
        g                 = dest if dest is not None else QuartoGame(self.twistCount, self.verbose)
        g.dims            = IntVector2(self.dims.x, self.dims.y)
        g.selectedPieces  = [piece for piece in self.selectedPieces]
        #g.selectedPieces  = np.copy(self.selectedPieces)
        g.board           = np.copy(self.board)
        #g.remainingPieces = [piece for piece in self.remainingPieces]
        g.remainingPieces = np.copy(self.remainingPieces)
        g.undoMemLength   = self.undoMemLength
        g.isWinningState  = self.isWinningState
        g.avaliableSquareCount = self.avaliableSquareCount
        g.remainingPieceCount = self.remainingPieceCount
        g.selectedPieceCount  = self.selectedPieceCount
        # Undo stack is not copied, to avoid exploding memory
        return g

    def squareIsEmpty(self, index:IntVector2) -> bool:
        return self.board[index] < 0

#========== Undo ============
#   Returns the state of this game to its previous game state.
#   Preserves undoStack, to allow for multiple undos
#   input:
#       numberOfUndos (int): How many moves to undo, default 1

    def undo(self, numberOfUndos=1) -> None:
        if numberOfUndos < 1:       return
        if len(self.undoStack) < 1: return

        newUndoStack   = self.undoStack[1:]
        prevState      = self.undoStack[0]
        prevState.copy(dest=self)
        self.undoStack = newUndoStack

#======= LogGameState ==================
#   Logs the current game state into undo memory.
    def logGameState(self) -> None:
        if self.undoMemLength < 1: return
        self.undoStack = [self.copy()] + self.undoStack[:self.undoMemLength-1]

#======== Select a given piece ==================
#   Inputs:
#       piece (int) : int representing the piece to be selected
#   Returns:
#       boolean : did the operation succeed
    def selectPiece(self, piece:int) -> bool:
        if piece < 0 or piece >= len(self.remainingPieces) or self.remainingPieces[piece] != 1:
            if self.verbose:
                print(f'Cannot select piece {piece} when remaining pieces are {self.remainingPieces}')
            return False
        if self.twistCount <= len(self.selectedPieces):
            if self.verbose:
                print(f'Cannot select another piece, there are {sum(self.remainingPieces)} already selected.')
            return False

        self.logGameState()
        self.selectedPieces.append(piece)
        #self.selectedPieces = np.append(self.selectedPieces, piece)
        self.remainingPieces[piece] = 0

        self.selectedPieceCount  += 1
        self.remainingPieceCount -= 1

        return True
    
    def deselectAll(self):
        for piece in self.selectedPieces:
            self.remainingPieceCount += 1
            self.remainingPieces[piece] = 1
        #self.selectedPieces  = np.array([], dtype=np.int32)
        self.selectedPieces = []
        self.selectedPieceCount = 0


#====== Places a given piece at a given index ============
#   Inputs: 
#       piece (int)        : int representing the piece to be placed
#       index (IntVector2) : index on the board indicating where to place the piece
#   Returns:
#       boolean: was the piece successfully placed.
    def placePiece(self, piece:int, index:IntVector2) -> None:
        if index.x < 0 or index.y < 0 or index.x >= self.dims.x or index.y >= self.dims.y:
            if self.verbose:
                print(f'Cannot place piece at invalid index X:{index[0]} Y:{index.y}')
            return False
        if self.board[index] >= 0:
            if self.verbose:
                print(f'Cannot place piece, square is occupied.')
            return False
        if piece not in self.selectedPieces:
            if self.verbose:
                print(f'Attempted to place a piece that is not selected.')
            return False

        self.logGameState()
        #self.board[index] = piece
        self.isWinningState = FastCannon.placePiece(self.board, index.x, index.y, piece)
        #pieceIndex = np.where(self.selectedPieces == piece)[0][0]
        #self.selectedPieces = np.delete(self.selectedPieces, pieceIndex)
        self.selectedPieces.pop(self.selectedPieces.index(piece))
        self.avaliableSquareCount -= 1
        self.deselectAll()

        #self.last_move = (index.x, index.y)
        #self.isWinningState = None # No longer know if is winning state

        return True
    
    # Removes piece at a given index, if one is there. 
    # Adds piece back to selected
    def removePiece(self, index:IntVector2) -> bool:
        if index.x < 0 or index.y < 0 or index.x >= self.dims.x or index.y >= self.dims.y:
            if self.verbose:
                print(f'Cannot place piece at invalid index X:{index[0]} Y:{index.y}')
            return False
        if self.board[index] < 0:
            if self.verbose:
                print(f'No piece to remove at this index.')
            return False
        #self.selectedPieces = np.append(self.selectedPieces, self.board[index])
        self.selectedPieces.append(self.board[index])
        self.selectedPieceCount += 1
        self.board[index] = -1
        self.avaliableSquareCount += 1
    
    def updateWinStatus(self, index):
        if self.isWinningState: return
        row = self.board[:, index.y]
        if self.checkFeatureList(row):
            self.isWinningState = True
            return
        col = self.board[index.x]
        if self.checkFeatureList(col):
            self.isWinningState = True
            return
        if index.x == index.y:
            diag = [self.board[i, i] for i in range(self.board.shape[0])]
            if self.checkFeatureList(diag):
                self.isWinningState = True
            return
        elif index.x + index.y == self.board.shape[0] - 1:
            diag = [self.board[i, (self.board.shape[0] - 1) - i] for i in range(self.board.shape[0])]
            if self.checkFeatureList(diag):
                self.isWinningState = True
            return

#====== Get Avaliable Squares ====================
#   Gets a list of squares that are avaliable to be played on
#   returns: [IntVector2]
    def getAvaliableSquares(self) -> list[IntVector2]:
        squares = []
        for y in range(self.board.shape[1]):
            for x in range(self.board.shape[0]):
                if self.board[x,y] < 0:
                    squares.append(IntVector2(x, y))
        return squares

    def getSelectedPieces(self) -> list[int]: return [piece for piece in self.selectedPieces]
    def getRemainingPieces(self) -> list[int]: 
        pieces = []
        for i in range(len(self.remainingPieces)):
            if self.remainingPieces[i] > 0:
                pieces.append(i)
        return pieces

    # Returns true if the board has a winning state on it.
    # Assumes the board is square
    def checkWin(self) -> bool:
        if self.isWinningState is not None:
            return self.isWinningState
        return False

    def checkWinFull(self):
        boardSize = self.board.shape[0]
        #Check rows
        for i in range(boardSize):
            if self.checkFeatureList(self.board[i]):
                return True
        #Check columns
        cols = np.transpose(self.board)
        for i in range(boardSize):
            if self.checkFeatureList(cols[i]):
                return True
        #Check Diagonal
        if self.checkFeatureList([self.board[i, i] for i in range(boardSize)]):
            return True
        if self.checkFeatureList([self.board[i, boardSize - (i+1)] for i in range(boardSize)]):
            return True

        return False
#========= CheckFeatureList ====================
#   checks a features list of ints to look for any common trait.
#   Returns true if any trait is share across all features.
    def checkFeatureList(self, feats:list[int]) -> bool:
        if min(feats) < 0:
            return False
        andCmp = int(math.pow(2, 16) - 1)
        orCmp  = 0
        for feat in feats:
            andCmp = andCmp & int(feat)
            orCmp  = orCmp  | int(feat)
        return andCmp != 0 or int(math.pow(2, len(feats)) - 1) - orCmp != 0


#========== Prints game in a human readable format =========
    def printGame(self):
        def numToBin(num, digs):
            if digs <= 0: return ""
            c = str(int(num) % 2)
            return numToBin(num // 2, digs-1) + c

        digits = int(math.log2(len(self.remainingPieces)))
        seperator = ""
        blank     = ""
        for _ in range(digits): 
            seperator += '-'
            blank     += ' '
        output = ""
        sepRow = ''
        for i in range(self.board.shape[0]):
            sepRow += seperator
            sepRow += "+"
        sepRow = sepRow[:-1]
        for y in range(self.board.shape[1]):
            for x in range(self.board.shape[0]):
                if self.board[x,y] < 0:
                    output += blank
                else:
                    output += numToBin(self.board[x,y], digits)
                output += '|'
            output = output[:-1]
            if y < self.board.shape[1] - 1:
                output += '\n' + sepRow + '\n'
        print(output)

#================ Hashes board into unique int ============================
    # Uses current board state to create a unique int as the board's hash
    # Considers only what spaces are occupied, and what they are occupied by
    # Does not consider selected pieces or remaining pieces
    # The resulting number can be up to the order of 2^80
    def hashBoard(self):
        digits = 4
        occupied = 0
        values = 0
        for y in range(self.dims.y):
            for x in range(self.dims.x):
                if self.board[x, y] >= 0:
                    values = (values << digits) | int(self.board[x,y])
                    occupied += 1
                occupied = occupied << 1
        occupied = occupied >> 1
        return (values << len(self.remainingPieces)) | occupied
    
    # -String interpretation, for bit overflow safety
    # def hashBoard(self):
    #     digits = 4
    #     occupied = ""
    #     values = ""
    #     for y in range(self.dims.y):
    #         for x in range(self.dims.x):
    #             if self.board[x, y] >= 0:
    #                 s = bin(int(self.board[x,y]))[2:]
    #                 while len(s) < digits: s = '0' + s
    #                 values += s
    #                 occupied += '1'
    #             else:
    #                 occupied += '0'
    #     return values + occupied

    # Old string implementation of loadFromHash
    #hard coded to board size of 4x4 for now
    # def loadFromHash(self, hash):
    #     occupied = hash[-16:]
    #     print(occupied)
    #     pieceValues = hash[:-16]
    #     print(pieceValues)
    #     pieces = [int(hash[i:i+4], 2) for i in range(0, len(pieceValues), 4)]
    #     print(pieces)
    #     for i in range(len(self.remainingPieces)):
    #         self.remainingPieces[i] = 0 if i in pieces else 1
    #     for y in range(self.dims.y):
    #         for x in range(self.dims.x):
    #             if occupied[y*4 + x] == '1':
    #                 self.board[IntVector2(x,y)] = pieces.pop(0)
    #             else:
    #                 self.board[IntVector2(x,y)] = -1
    #     self.isWinningState = self.checkWinFull()

    # loadHash that uses 80bit hash to restore game state
    def loadFromHash(self, boardHash):
        values = boardHash >> 16  # Extract the first 64 bits (piece values)
        occupied = boardHash & 0xFFFF  # Extract the last 16 bits (occupied squares)

        self.board.fill(-1)
        self.remainingPieces.fill(1)

        self.remainingPieceCount = 16
        self.avaliableSquareCount = 16

        # Extract 16 pieces from LSB
        piece_list = []
        for _ in range(16):  
            piece_list.append(values & 0b1111)
            values >>= 4

        # Reconstruct the board
        piece_index = 0
        for y in range(self.dims.y - 1, -1, -1):
            for x in range(self.dims.x - 1, -1, -1):
                bit_position = (y * self.dims.x) + x
                if (occupied >> (15 - bit_position)) & 1:
                    self.board[IntVector2(x, y)] = piece_list[piece_index]
                    self.remainingPieces[piece_list[piece_index]] = 0
                    piece_index += 1
                    self.avaliableSquareCount -= 1
                    self.remainingPieceCount -= 1

        self.isWinningState = self.checkWinFull()

    """
    Populates the board with a given number of pieces (0-8) ensuring no winning row/col/diag exists.

    Parameters:
        pieceCount (int): Number of pieces to place on the board.

    Ensures no winning conditions exist after placement.
    """
    def populateBoard(self, pieceCount: int):
        placed = 0

        while placed < pieceCount:

            piece = random.choice(self.getRemainingPieces())
            square = random.choice(self.getAvaliableSquares())

            # Place the piece
            if self.selectPiece(piece):
                self.placePiece(piece, square)

                # Check if the placement caused a win
                if self.checkWin():
                    # If there's a win, undo and try again
                    self.undo(2)
                else:
                    placed += 1
            else:
                self.undo()

        if self.verbose:
            print(f"Board populated with {placed} pieces, ensuring no winning lines.")
            self.printGame()
            self.printRemainingPieces()
            print()

    def printRemainingPieces(self):
        remaining = self.getRemainingPieces()
        def pieceToBinaryString(piece):
            return f'{piece:04b}'  # Convert to 4-bit binary (assuming 4 traits per piece)

        if remaining:
            print("Remaining Pieces:")
            print(", ".join(pieceToBinaryString(piece) for piece in remaining))
        else:
            print("No remaining pieces.")

    # Performs XOR operation using the given XORpiece on the selected and remaining pieces
    def xorPieces(self, xorPiece):
        if xorPiece < 0 or xorPiece >= len(self.remainingPieces):
            return
        for i in range(len(self.selectedPieces)):
            self.selectedPieces[i] = self.selectedPieces[i] ^ xorPiece

        newRemPieces = [0] * len(self.remainingPieces)
        for i in range(len(self.remainingPieces)):
            if self.remainingPieces[i] > 0:
                index = i ^ xorPiece
                newRemPieces[index] = 1
        self.remainingPieces = newRemPieces

# Test to see if hash is working as expected
# g = QuartoGame(twistCount=1)
# g.populateBoard(8)
# g.printRemainingPieces()
# hash = g.hashBoard()
# print(f'Hash: {hash:04b}')
# g.loadFromHash(hash)
# g.printGame()
