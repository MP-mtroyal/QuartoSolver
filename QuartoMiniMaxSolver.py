from QuartoGame import QuartoGame
from BasicQuartoCannon import BasicQuartoCannon
import math

"""
MiniMaxSolver implements a Minimax algorithm with memoization to solve the game of Quarto.
It handles both placing a piece and choosing a piece for the opponent, considering a 
specified search depth.
"""
class QuartoMiniMaxSolver:

    """
    Initializes the MiniMaxSolver with a given search depth (32 for full game).
    Initializes memoization table and a game cannonizer to optimize game state hashing.

    Parameters:
        depth (int): Maximum search depth minimax will go to. (32 for full game)
    """
    def __init__(self, depth=16):
        self.memoTable = {}
        self.depth = depth
        self.cannonizer = BasicQuartoCannon()


    """ placePiece()
    Determines and places the best piece (provided by the opponent) on the game board.
    This method calls minimax() to search for the optimal placement.

    Determines the best square to place the currently selected piece using the minimax 
    algorithm. Places the piece in the chosen square on the game board.

    Parameters:
        game (QuartoGame): The current state of the game.
    """
    def placePiece(self, game: QuartoGame) -> None:
        score, _, square, moves = self.miniMax(game, self.depth, True, True)
        print("Placement Path: ", end="")
        print(moves)
        print()
        if square is not None:
            game.placePiece(game.selectedPieces[0], square)
        else:
            print("Square WAS NONE: You shouldn't see this")


    """ choosePiece()
    Determines the best piece to give to the opponent using the minimax algorithm.
    Selects the chosen piece for the opponent's turn.

    Parameters:
        game (QuartoGame): The current state of the game.
    """
    def choosePiece(self, game: QuartoGame) -> None:
        score, piece, _, moves = self.miniMax(game, self.depth, True, False)
        print("Placement Path: ", end="")
        print(moves)
        print()
        if piece is not None:
            game.selectPiece(piece)
        else:
            print("PIECE WAS NONE: You shouldn't see this")


    """ miniMax()
    Recursive minimax function with memoization.
    Explores all possible game states to determine the optimal move.
    Determines the best move for a current piece or best piece to give to the opponent.
    
    Parameters:
        game (QuartoGame): Current game state.
        depth (int): Remaining depth to search.
        turn (bool): True if it's this AI's turn, False if it's the opponent's.
        placingPiece (bool): True if this phase is placing a piece, False if it's choosing a piece.

    Returns:
        Tuple: (best score, best piece (when choosing), best square (when placing), move path as string)
    """
    def miniMax(
            self,
            game: QuartoGame,
            depth: int,
            turn: bool,
            placingPiece: bool
    ):
        if depth == 0 or game.checkWin() or len(game.getAvaliableSquares()) == 0 or len(game.getRemainingPieces()) == 0:
            gameState = self.eval(game, turn)
            return gameState, None, None, " Score:" + str(gameState)
        cannonGame = self.cannonizer.cannonizeGame(game)
        gameHash = cannonGame.hashBoard()
        

        if placingPiece:
            """ Place Piece
            Handles placing a piece on the board. Iterates over all available squares
            and recursively evaluates the score for each possible placement.
            """
            if len(game.selectedPieces) == 0:
                print("ERROR: NO SELECTED PIECES to be placed")
                return

            bestMoves, bestSquare, bestScore = None, None, -math.inf
            moves = None
            currPiece = game.selectedPieces[0]
            pieceHash = (gameHash, currPiece)
            if pieceHash in self.memoTable:
                score, move, square, moveStr = self.memoTable[pieceHash]
                #if not turn:
                #    score *= -1
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

        else:
            """ Choose Piece
            Handles selecting a piece for the opponent. Iterates over all remaining pieces
            and recursively evaluates the score for each choice.
            """
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


    """
    Evaluates the current game state to return a score.
    A winning board state returns +1 for the AI, -1 for the opponent.
    Non-terminal and stalemate states return 0.

    Parameters:
        game (QuartoGame): Current game state.
        turn (bool): True if it's this AI's turn.

    Returns:
        score (int): (1, -1, or 0).
    """
    def eval(self, game: QuartoGame, turn: bool):
        if game.checkWin():
            return 1 if turn else -1
        return 0