import numpy as np

#======= Initialize Test Array ==========#
arr = np.array([[0, 1, 2, 3],
                [4, 5, -1, 7],
                [8, -1, 10, 11],
                [12, 13, 14, -1]])

#======= loadAGLTransforms ==========#
# Loads 4x4 transformations from the AGL(2,4) file.
def loadAGLTransforms(filename="affineMaps/agl_2_4_maps.txt"):
    transforms = []
    with open(filename, "r") as f:
        for line in f:
            transforms.append(eval(line.strip()))  # parse string to list
    return transforms

#======= applyAGLTransform ==========#
# Applies a position remapping using the transformation.
def applyAGLTransform(board, transform):
    flat_board = board.flatten()
    result = np.full(16, -1)  # fill with -1s
    for i in range(16):
        dst = transform[i]  # move value at index i to dst
        result[dst] = flat_board[i]
    return result.reshape(4, 4)

#======= getTransformedBoardsFromAGL ==========#
# Applies all 2880 AGL transformations to the board.
def getTransformedBoardsFromAGL(board, transforms):
    boards = []
    for t in transforms:
        flat_transform = sum(t, [])  # flatten 4x4 grid to 16-element list
        transformed = applyAGLTransform(board, flat_transform)
        boards.append(transformed)
    return boards

#======= remove_duplicate_arrays ==========#
# Removes duplicate 4x4 numpy arrays from a list using hashing.
def remove_duplicate_arrays(arr_list):
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
def evaluateBoard(board):
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
def getCanditateBoards(boards):
    candidate1, candidate2 = [], []

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

#======= getXOR ==========#
# Chooses a normalization base (first non -1 value in top-left).
def getXOR(board):
    return board[0, 0] if board[0, 0] != -1 else board[0, 1]

#======= boardXOR ==========#
# Applies XOR normalization to all non -1 elements.
def boardXOR(board, value):
    new_arr = board.copy()
    mask = (new_arr != -1)
    new_arr[mask] = new_arr[mask] ^ value
    return new_arr

#======= best_board ==========#
# Selects the board with the lowest evaluation score.
def best_board(boards):
    return min(boards, key=evaluateBoard)

#======= cannonizeGame ==========#
# Uses AGL(2,4) transformations to find the canonical version of a board.
def cannonizeGame(board):
    agl_transforms = loadAGLTransforms()
    transformations = getTransformedBoardsFromAGL(board, agl_transforms)
    cBoard = getCanditateBoards(transformations)
    toBeEval = []
    for board in cBoard:
        toBeEval.append(boardXOR(board, getXOR(board)))
    return best_board(toBeEval)

