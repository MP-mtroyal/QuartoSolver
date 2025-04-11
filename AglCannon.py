from QuartoGame import QuartoGame
from Affine4Game import Affine4Game
from QuartoCannon import QuartoCannon
import numpy as np

class AglCannon(QuartoCannon):
    def __init__(self):
        super().__init__()

        self.agl_transforms = self.loadAGLTransforms()

    #======= loadAGLTransforms ==========#
    # Loads 4x4 transformations from the AGL(2,4) file.
    def loadAGLTransforms(self, filename="affineMaps/agl_2_4_maps.txt"):
        transforms = []
        with open(filename, "r") as f:
            for line in f:
                transforms.append(eval(line.strip()))  # parse string to list
        return transforms

    #======= applyAGLTransform ==========#
    # Applies a position remapping using the transformation.
    def applyAGLTransform(self, board, transform):
        flat_board = board.flatten()
        result = np.full(16, -1)  # fill with -1s
        for i in range(16):
            dst = transform[i]  # move value at index i to dst
            result[dst] = flat_board[i]
        return result.reshape(4, 4)

    #======= getTransformedBoardsFromAGL ==========#
    # Applies all 2880 AGL transformations to the board.
    def getTransformedBoardsFromAGL(self, board, transforms):
        boards = []
        for t in transforms:
            flat_transform = sum(t, [])  # flatten 4x4 grid to 16-element list
            transformed = self.applyAGLTransform(board, flat_transform)
            boards.append(transformed)
        return boards

    #======= remove_duplicate_arrays ==========#
    # Removes duplicate 4x4 numpy arrays from a list using hashing.
    def remove_duplicate_arrays(self, arr_list):
        unique_arrays = []
        seen = set()
        for arr in arr_list:
            arr_hash = arr.tobytes()
            if arr_hash not in seen:
                unique_arrays.append(arr)
                seen.add(arr_hash)
        return unique_arrays

    #======= evaluateBoard ==========#
    # Flattens a board and computes a score by bit-packing values (skip -1).
    def evaluateBoard(self, board):
        flat = board.flatten()
        result = 0
        for i in range(1, len(flat)):
            shift = 4 * (i - 1)
            val = int(flat[i])
            addition = 0 if val == -1 else val << shift
            result += addition
        return result

    #======= getCanditateBoards ==========#
    # Splits board list into two categories and returns best candidate set.
    def getCanditateBoards(self, boards):
        candidates = []

        for board in boards:
            if board[0, 0] == 0:
                candidates.append(board)

        if len(candidates) > 0:
            return candidates
        else:
            return [np.full((4, 4), -1)]

    #======= best_board ==========#
    # Selects the board with the lowest evaluation score.
    def best_board(self, boards):
        return min(boards, key=self.evaluateBoard)

    #======= cannonizeGame ==========#
    # Uses AGL(2,4) transformations to find the canonical version of a board.
    def cannonizeGame(self, game:Affine4Game) -> Affine4Game:
        game = game.copy()
        board = game.board
        transformations = self.getTransformedBoardsFromAGL(board, self.agl_transforms)
        cBoard = self.getCanditateBoards(transformations)
        game.board = self.best_board(cBoard)
        return game


