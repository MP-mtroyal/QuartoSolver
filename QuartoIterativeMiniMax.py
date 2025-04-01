import multiprocessing.pool
from QuartoGame import QuartoGame
from BasicQuartoCannon import BasicQuartoCannon
from GreatQuartoCannon import GreatQuartoCannon
from QuartoCannon import QuartoCannon
import math
from Profiler import Profiler
import time
import multiprocessing
import pickle
from QuartoDataTypes import IntVector2

"""
MiniMaxSolver implements a Minimax algorithm with memoization to solve the game of Quarto.
It handles both placing a piece and choosing a piece for the opponent, considering a 
specified search depth.
"""
class QuartoIterativeMiniMax:

    """
    Initializes the MiniMaxSolver with a given search depth (32 for full game).
    Initializes memoization table and a game cannonizer to optimize game state hashing.

    Parameters:
        depth (int): Maximum search depth minimax will go to. (32 for full game)
    """
    def __init__(self, depth=16):
        self.memoTable = {}
        self.cannonTable = {}
        self.toCannonize = {}
        self.depth = depth
        self.cannonizer  = GreatQuartoCannon()
        self.naiveCannon = BasicQuartoCannon()
        self.profiler    = Profiler()
        self.exploredCounter = 0
        self.memoedCounter = 0
        self.bredthCount = [0] * 33
        self.bredthMax = 5000

        self.currDepth = 0

        self.memoTablePath = "memoTables/"
        #self.loadCannonTable()

    def saveCannonTable(self):
        # try:
        canonList = []
        for key in self.cannonTable.keys():
            canonList.append((key, self.cannonTable[key].hashBoard()))
        #print(canonList)
        with open(self.memoTablePath + "canonTable.pkl", 'ab') as f:
            pickle.dump(canonList, f)
        # except:
        #     print("Could not save canon table")

    def loadCannonTable(self):
        try:
            with open(self.memoTablePath + "canonTable.pkl", 'rb') as f:
                self.cannonTable = pickle.load(f)
            print(self.cannonTable)
        except:
            print("Could not open cannon table")


    """ placePiece()
    Determines and places the best piece (provided by the opponent) on the game board.
    This method calls minimax() to search for the optimal placement.

    Determines the best square to place the currently selected piece using the minimax 
    algorithm. Places the piece in the chosen square on the game board.

    Parameters:
        game (QuartoGame): The current state of the game.
    """
    def placePiece(self, game: QuartoGame) -> None:
        prevMemLength = game.undoMemLength
        game.undoMemLength = 0
        self.profiler.fullReset()
        for i in range(1, self.depth + 1):
            self.memoTable = {} # reset memo table, it only memoizes up to a given depth
            score, _, square, moves = self.miniMax(game, i, True, True)
            if len(self.toCannonize) > 0:
                print(f'Canonizing {len(self.toCannonize)} boards.')
                for key in self.toCannonize.keys():
                    currGame = self.toCannonize[key]
                    cannonGame = self.cannonizer.cannonizeGame(currGame)
                    self.cannonTable[currGame.hashBoard()] = cannonGame
                self.toCannonize = {}

        print("Placement Path: ", end="")
        print(moves)
        print(f'Explored: {self.exploredCounter} | Memoed: {self.memoedCounter} | MemoTable: {len(self.memoTable.keys())}')
        print()
        if square is not None:
            game.placePiece(game.selectedPieces[0], square)
        else:
            print("Square WAS NONE: You shouldn't see this")
        game.undoMemLength = prevMemLength


    """ choosePiece()
    Determines the best piece to give to the opponent using the minimax algorithm.
    Selects the chosen piece for the opponent's turn.

    Parameters:
        game (QuartoGame): The current state of the game.
    """
    def choosePiece(self, game: QuartoGame) -> None:
        prevMemLength = game.undoMemLength
        game.undoMemLength = 0
        self.profiler.fullReset()
        for i in range(1, self.depth + 1):
            self.bredthCount = [0] * 33

            startTime = time.time()
            self.memoTable = {} # reset memo table, it only memoizes up to a given depth
            score, piece, square, moves = self.miniMax(game, i, True, False)
            
            #if i % 2 == 0:
            print(f'----------------- Depth:{i} ------------------')
            print(f'   --- {self.bredthCount[1]} became {len(self.toCannonize)} boards')
            print('      ---         ---          ---       ---')

            self.profiler.pause()
            self.cannonizeSavedBoards()
            print(f'Executed step in {(time.time() - startTime) :.05f}')
            startTime = time.time()
        print("\n")

        self.printMinimaxData(moves)
        if piece is not None: game.selectPiece(piece)
        else: print("PIECE WAS NONE: You shouldn't see this")

        game.undoMemLength = prevMemLength

    # Not currently functional, commented out for safety
    # def populateCannontableParallel(self, game: QuartoGame, numPieces) -> None:
    #     prevMemLength = game.undoMemLength
    #     game.undoMemLength = 0
        
    #     maxWorkers = 4

    #     gamesLayer = [game]
    #     self.profiler.fullReset()
    #     for i in range(1, numPieces+1):
    #         print("----------------------------------------")
    #         startTime = time.time()
    #         self.memoTable = {} # reset memo table, it only memoizes up to a given depth
            
    #         for g in gamesLayer:
    #             score, piece, square, moves = self.miniMax(g, 2, True, False)
            
    #         self.profiler.pause()
    #         if len(self.toCannonize) > 1:
    #             gamesLayer = self.cannonizeSavedBoards()
    #         else:
    #             print("Something went wrong, there are no boards to cannonize")
    #         print(f'Executed step in {(time.time() - startTime) :.05f}')
    #         startTime = time.time()

    #     print("\n")
    #     print(f'Cannon Table size: {len(self.cannonTable)}')

    #     self.printMinimaxData(moves)
        
    #     if piece is not None: game.selectPiece(piece)
    #     else: print("PIECE WAS NONE: You shouldn't see this")

    #     game.undoMemLength = prevMemLength


    # Saves the boards logged in the 'toCannonize' board
    # as boardHash : canonizedGame pairs in the cannonTable
    # Clears toCannonize, and count how many new boards are added
    def cannonizeSavedBoards(self):
        if len(self.toCannonize) > 0:
            print(f'Canonizing {len(self.toCannonize)} boards.')
            newCanonBoards = set()
            cannonGames = []

            for key in self.toCannonize.keys():
                self.profiler.unpause()

                self.profiler.log("Reading Memo")
                currGame     = self.toCannonize[key]


                self.profiler.log("Cannonizing")
                cannonGame   = self.cannonizer.cannonizeGame(currGame)

                self.profiler.log("Storing Hash")
                self.cannonTable[currGame.hashBoard()] = cannonGame
                cannonHash = cannonGame.hashBoard()

                if cannonHash not in newCanonBoards:
                    newCanonBoards.add(cannonGame.hashBoard())
                    cannonGames.append(cannonGame)

            print(f'Added {len(newCanonBoards)} new boards.')
            self.toCannonize = {}
            return cannonGames
        return []

    def printMinimaxData(self, moves):
        print("Placement Path: ", end="")
        print(moves)
        print(f'Explored: {self.exploredCounter} | Memoed: {self.memoedCounter} | MemoTable: {len(self.memoTable.keys())}')
        print()
        self.profiler.print()

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
        self.profiler.log("Hashing")
        gameHash = game.hashBoard()

        #Game has been canonized already
        self.profiler.log("Checking Memo")
        if gameHash in self.cannonTable:
            if not placingPiece: # only canonize a board with no selected pieces
                self.profiler.log("Reading Memo")
                game = self.cannonTable[gameHash] # get canonized game
                self.profiler.log("Copying Game")
                game = game.copy() # copy game for safety
                game.deselectAll()
                self.profiler.log("Hashing")
                gameHash = game.hashBoard() # replace hash with canon hash

        #store game to be canonized
        else:
            self.profiler.log("Copying Game")
            copyGame = game.copy()
            copyGame.deselectAll()
            self.profiler.log("Storing hash")
            self.toCannonize[gameHash] = copyGame


        self.profiler.log("Checking Depth")
        if game.checkWin():
            self.profiler.log("Return")
            return 1, None, None, "Score:1"
        if depth == 0 or game.avaliableSquareCount <= 0 or game.remainingPieceCount <= 0:

            self.profiler.log("Return")
            return 0, None, None, " Score:0"

        

        if placingPiece:
            """ Place Piece
            Handles placing a piece on the board. Iterates over all available squares
            and recursively evaluates the score for each possible placement.
            """
            self.profiler.log("Basic Math")
            if len(game.selectedPieces) == 0:
                print("ERROR: NO SELECTED PIECES to be placed")
                return

            bestMoves, bestSquare, bestScore = None, None, -math.inf
            moves = None
            currPiece = game.selectedPieces[0]
            pieceHash = (gameHash, currPiece)

            self.profiler.log("Checking Memo")
            if pieceHash in self.memoTable:

                self.profiler.log("Reading Memo")
                score, move, square, moveStr = self.memoTable[pieceHash]
                
                self.profiler.log("Basic math")
                self.memoedCounter += 1

                self.profiler.log("Return")
                return score, move, square, moveStr
            
            # ============================================================
            self.profiler.log("Basic Math")
            if self.bredthMax is not None:
                if depth != 0:
                    if self.bredthCount[depth] >= self.bredthMax:
                        return 0, 15, IntVector2(0, 0), "Dummy"
                    self.bredthCount[depth] += 1
            # ============================================================
            
            self.exploredCounter += 1

            self.profiler.log("Avaliable Squares")
            for square in game.getAvaliableSquares():

                self.profiler.log("Copying Game")
                nextGame = game.copy()
                
                self.profiler.log("Placing Piece")
                if not nextGame.placePiece(currPiece, square):
                    print("FAILED TO PLACE")

                self.profiler.log("Calling")
                score, _, _, moves = self.miniMax(nextGame, depth-1, turn, False)

                self.profiler.log("Basic Math")
                if score > bestScore:
                    bestScore = score
                    bestSquare = square
                    bestMoves = moves

            self.profiler.log("Storing Hash")
            moveStr = f'({bestSquare.x},{bestSquare.y})' + "->" + bestMoves
            self.memoTable[pieceHash] = [bestScore, currPiece, bestSquare, moveStr]

            self.profiler.log("Calling")
            return bestScore, None, bestSquare, moveStr

        else:
            """ Choose Piece
            Handles selecting a piece for the opponent. Iterates over all remaining pieces
            and recursively evaluates the score for each choice.
            """
            self.profiler.log("Basic Math")
            pieceHash = (gameHash, None)

            self.profiler.log("Checking Memo")
            if pieceHash in self.memoTable:

                self.profiler.log("Reading Memo")
                self.memoedCounter += 1
                score, move, square, moveStr = self.memoTable[pieceHash]
                
                self.profiler.log("Return")
                return score, move, square, moveStr
            
            # ============================================================
            self.profiler.log("Basic Math")
            if self.bredthMax is not None:
                if depth != 0:
                    if self.bredthCount[depth] >= self.bredthMax:
                        return 0, 15, IntVector2(0, 0), "Dummy"
                    self.bredthCount[depth] += 1
            # ============================================================

            bestMoves, bestSquare, bestPiece, bestScore = None, None, None, -math.inf
            moves = None

            self.profiler.log("Getting Remaining Pieces")
            for piece in game.getRemainingPieces():
                
                self.profiler.log("Checking Memo")
                pieceHash = (gameHash, piece)
                if pieceHash in self.memoTable:

                    self.profiler.log("Reading Memo")
                    score, _, square, moves = self.memoTable[pieceHash]
                    self.memoedCounter += 1

                else:
                    # self.profiler.log("Copying Game")
                    # nextGame = game.copy()

                    self.profiler.log("Selecting Piece")
                    if not game.selectPiece(piece):
                        print("FAILED TO SELECT")

                    self.profiler.log("Calling")
                    score, _, square, moves = self.miniMax(game, depth-1, not turn, True)

                    self.profiler.log("Deselecting")
                    game.deselectAll()

                self.profiler.log("Basic Math")
                score *= -1

                if score > bestScore:
                    bestScore  = score
                    bestPiece  = piece
                    bestMoves  = moves
                    bestSquare = square

            self.profiler.log("Storing Hash")
            moveStr = str(bestPiece) + "->" + bestMoves
            pieceHash = (gameHash, None) #Best possible score, no piece selected
            self.memoTable[pieceHash] = [bestScore, bestPiece, bestSquare, moveStr]
            self.exploredCounter += 1

            self.profiler.log("Return")
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
    
