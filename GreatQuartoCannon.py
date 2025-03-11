from QuartoGame import QuartoGame
from QuartoCannon import QuartoCannon
from QuartoDataTypes import IntVector2
import numpy as np

class GreatQuartoCannon(QuartoCannon):
    def __init__(self):
        super().__init__()

    def reset(self):
        return super().reset()

    #======= boxRotate ==========
    # Swaps row 1<->2 and row 3<->4,
    # then swaps col 1<->2 and col 3<->4.
    # This maintains the board structure in a meaningfully different arrangement.
    def boxRotate(self, board):
        swapped_rows = board[[1, 0, 3, 2], :]
        result = swapped_rows[:, [1, 0, 3, 2]]
        return result

    #======= innerRotate ==========
    # Swaps row 2<->3 and col 2<->3.
    # This maintains the board structure in a meaningfully different arrangement.
    def innerRotate(self, board):
        swapped_rows = board[[0, 2, 1, 3], :]
        result = swapped_rows[:, [0, 2, 1, 3]]
        return result

    #======= diagonalReflect ==========
    # Returns the reflection of the board along its main diagonal.
    def diagonalReflect(self, board):
        return board.transpose()

    #======= verticalReflect ==========
    # Returns the reflection of the board along its vertical axis.
    def verticalReflect(self, board):
        return np.flip(board, axis=1)

    #======= horizontalReflect ==========
    # Returns the reflection of the board along its horizontal axis.
    def horizontalReflect(self, board):
        return np.flip(board, axis=0)

    #======= rotate ==========
    # Returns the board rotated 90° counterclockwise.
    def rotate(self, board):
        return np.rot90(board)

    #======= getBaseStruct ==========
    # Applies the set of non-D4 transformations for all equivalent Quarto base boards.
    # Expects a 4x4 numpy array.
    def getBaseStruct(self, board):
        semifinal = []
        semifinal.append(board)
        semifinal.append(self.boxRotate(board))
        semifinal.append(self.innerRotate(board))
        semifinal.append(self.innerRotate(self.boxRotate(board)))
        return semifinal

    #======= d4Tranformation ==========
    # Applies D4 (dihedral group) transformations to a square board.
    # Expects a 2D numpy array.
    def d4Tranformation(self, board):
        nextlist = []
        for item in board:
            nextlist.append(item)
            nextlist.append(self.rotate(item))
            nextlist.append(self.rotate(self.rotate(item)))
            nextlist.append(self.rotate(self.rotate(self.rotate(item))))
            nextlist.append(self.verticalReflect(item))
            nextlist.append(self.horizontalReflect(item))
            nextlist.append(self.diagonalReflect(item))
            nextlist.append(self.verticalReflect(self.horizontalReflect(self.diagonalReflect(item))))
        return nextlist

    #======= remove_duplicate_arrays ==========
    # Removes duplicate 4x4 numpy arrays from a list.
    # Uses a bytes representation to hash each array.
    def remove_duplicate_arrays(self, arr_list):
        unique_arrays = []
        seen = set()
        for arr in arr_list:
            # Convert the array to a bytes representation.
            arr_hash = arr.tobytes()
            if arr_hash not in seen:
                unique_arrays.append(arr)
                seen.add(arr_hash)
        return unique_arrays

    #======= evaluateBoard ==========
    # Evaluates a 4x4 board by flattening it and summing its elements with bit shifting.
    # Skips the first element; for subsequent elements, shifts left by an increment of 4 bits.
    # If an element is -1, adds 0 instead.
    def evaluateBoard(self, board):
        flat = board.flatten()
        result = 0
        for i in range(1, len(flat)):
            shift = 4 * (i - 1)  # Second element: shift=0; third: shift=4; etc.
            val = int(flat[i])
            if val == -1:
                addition = 0
            else:
                addition = val << shift
            result += addition
        return result
    
    def badBoardEval(self, board):
        digits = 4
        occupied = 0
        values = 0
        for y in range(board.shape[0]):
            for x in range(board.shape[1]):
                if board[x, y] >= 0:
                    values = (values << digits) + int(board[x,y])
                    occupied += 1
                occupied = occupied << 1
        occupied = occupied >> 1
        return (values << (digits ** 2)) + occupied

    #======= getCanditateBoards ==========
    # Separates a list of 4x4 boards into candidate lists:
    #   - candidate1: boards whose [0, 0] element is not -1.
    #   - candidate2: boards whose [0, 0] is -1 but [0, 1] is not -1.
    # Returns candidate1 if non-empty; else candidate2 if non-empty;
    # otherwise, returns a 4x4 board of -1's.
    def getCanditateBoards(self, boards):
        candidate1 = []
        candidate2 = []
        
        for board in boards:
            if board[0, 0] != -1:
                candidate1.append(board)
            elif board[0, 1] != -1:
                candidate2.append(board)
        
        if candidate1:
            return candidate1
        elif candidate2:
            return candidate2
        else:
            return [np.full((4, 4), -1)]

    #======= getXOR ==========
    # Returns a value used for XOR normalization based on the board's first two elements.
    # If the first element is not -1, returns board[0,0]; otherwise, returns board[0,1].
    def getXOR(self, board):
        if board[0, 0] != -1:
            return board[0, 0]
        else:
            return board[0, 1]

    #======= boardXOR ==========
    # Returns a new board with each non -1 element XORed with the given value.
    # Elements equal to -1 remain unchanged.
    def boardXOR(self, board, value):
        new_arr = board.copy()           # Create a copy to avoid modifying the original.
        mask = (new_arr != -1)           # Boolean mask for elements not equal to -1.
        new_arr[mask] = new_arr[mask] ^ value  # Apply XOR on masked elements.
        return new_arr

    #======= best_board ==========
    # Returns the board with the minimum evaluation value from a list of boards.
    def best_board(self, boards):
        return min(boards, key=self.evaluateBoard)

    #======= cannonizeGame ==========
    # Canonicalizes a game board by applying D4 transformations, candidate selection,
    # and XOR normalization, then returns the best board based on evaluation.
    def cannonizeGame(self, game):
        game = game.copy()
        gameBoard = game.board.astype(np.int32)
        transformations = self.d4Tranformation(self.getBaseStruct(gameBoard))
        cBoard = self.getCanditateBoards(transformations)
        toBeEval = []
        for board in cBoard:
            toBeEval.append(self.boardXOR(board, self.getXOR(board)))
        game.board = self.best_board(toBeEval)
        game.xorPieces(self.getXOR(game.board))
        return game
