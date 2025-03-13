from QuartoGame import QuartoGame
from BasicQuartoCannon import BasicQuartoCannon
from GreatQuartoCannon import GreatQuartoCannon
from QuartoCannon import QuartoCannon
import math
from Profiler import Profiler

import time

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
        self.cannonTable = {}
        self.depth = depth
        #self.cannonizer = QuartoCannon()
        #self.cannonizer = BasicQuartoCannon()
        self.cannonizer = GreatQuartoCannon()
        self.profiler   = Profiler()
        self.exploredCounter = 0
        self.memoedCounter = 0


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
        print(f'Explored: {self.exploredCounter} | Memoed: {self.memoedCounter} | MemoTable: {len(self.memoTable.keys())}')
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
        self.profiler.fullReset()
        score, piece, _, moves = self.miniMax(game, self.depth, True, False)
        print("Placement Path: ", end="")
        print(moves)
        print(f'Explored: {self.exploredCounter} | Memoed: {self.memoedCounter} | MemoTable: {len(self.memoTable.keys())}')
        print()
        self.profiler.print()
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
            self.profiler.unpause()
            self.profiler.log("Evaluating Board")
            gameState = self.eval(game, turn)
            self.profiler.pause()
            return gameState, None, None, " Score:" + str(gameState)

        self.profiler.unpause()
        self.profiler.log("Hashing")
        #basicGameHash = game.hashBoard()

        self.profiler.log("Checking Memo")
        # if basicGameHash in self.cannonTable:

        #     self.profiler.log("Reading Memo")
        #     gameHash = self.cannonTable[basicGameHash]
        #     self.profiler.pause()

        # print("------------------------")
        #else:
        # game.printGame()
        # time.sleep(0.01)
        self.profiler.log("Cannonizing")
        #cannonGame = self.cannonizer.cannonizeGame(game)
        game = self.cannonizer.cannonizeGame(game)

        self.profiler.log("Hashing")
        #gameHash = cannonGame.hashBoard()
        gameHash = game.hashBoard()
        

        # self.profiler.log("Storing Hash")
        # self.cannonTable[basicGameHash] = gameHash
        self.profiler.pause()
        # game.printGame()
        # time.sleep(0.01)
        # print("=============================")

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

            self.profiler.unpause()
            self.profiler.log("Checking Memo")
            if pieceHash in self.memoTable:

                self.profiler.log("Reading Memo")
                score, move, square, moveStr = self.memoTable[pieceHash]
                self.profiler.pause()

                self.memoedCounter += 1
                return score, move, square, moveStr
            
            self.exploredCounter += 1
            self.profiler.log("Avaliable Squares")
            for square in game.getAvaliableSquares():

                self.profiler.log("Copying Game")
                nextGame = game.copy()
                
                self.profiler.log("Placing Piece")
                if not nextGame.placePiece(currPiece, square):
                    print("FAILED TO PLACE")
                self.profiler.pause()

                score, _, _, moves = self.miniMax(nextGame, depth-1, turn, False)

                self.profiler.unpause()
                self.profiler.log("Basic Math")
                if not turn:
                    score *= -1

                if score > bestScore:
                    bestScore = score
                    bestSquare = square
                    bestMoves = moves
                self.profiler.pause()

            self.profiler.unpause()
            self.profiler.log("Storing Hash")
            moveStr = f'({bestSquare.x},{bestSquare.y})' + "->" + bestMoves
            self.memoTable[pieceHash] = [bestScore, currPiece, bestSquare, moveStr]
            self.profiler.pause()

            return bestScore, None, bestSquare, moveStr

        else:
            """ Choose Piece
            Handles selecting a piece for the opponent. Iterates over all remaining pieces
            and recursively evaluates the score for each choice.
            """
            pieceHash = (gameHash, None)
            if pieceHash in self.memoTable:
                self.memoedCounter += 1
                return self.memoTable[pieceHash]

            bestMoves, bestSquare, bestPiece, bestScore = None, None, None, -math.inf
            moves = None

            self.profiler.unpause()
            self.profiler.log("Getting Remaining Pieces")
            for piece in game.getRemainingPieces():
                
                self.profiler.log("Checking Memo")
                pieceHash = (gameHash, piece)
                if pieceHash in self.memoTable:
                    self.profiler.log("Reading Memo")
                    score, _, square, moves = self.memoTable[pieceHash]
                    self.memoedCounter += 1
                else:
                    self.profiler.log("Copying Game")
                    nextGame = game.copy()

                    self.profiler.log("Selecting Piece")
                    if not nextGame.selectPiece(piece):
                        print("FAILED TO SELECT")
                    self.profiler.pause()

                    score, _, square, moves = self.miniMax(nextGame, depth-1, not turn, True)

                self.profiler.unpause()
                self.profiler.log("Basic Math")
                if turn:
                    score *= -1

                if score > bestScore:
                    bestScore  = score
                    bestPiece  = piece
                    bestMoves  = moves
                    bestSquare = square
                self.profiler.pause()

            self.profiler.unpause()
            self.profiler.log("Storing Hash")
            moveStr = str(bestPiece) + "->" + bestMoves
            pieceHash = (gameHash, None) #Best possible score, no piece selected
            self.memoTable[pieceHash] = [bestScore, bestPiece, bestSquare, moveStr]
            self.profiler.pause()

            self.exploredCounter += 1
            return bestScore, bestPiece, square, moveStr


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