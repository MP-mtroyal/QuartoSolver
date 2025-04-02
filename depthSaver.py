from QuartoGame import QuartoGame
from Affine4Game import Affine4Game
from GreatQuartoCannon import GreatQuartoCannon
from Affine4Cannon import Affine4Cannon
import time
from QuartoDataTypes import IntVector2

def hasDup(game: QuartoGame):
    counts = [0] * 16
    for y in range(game.board.shape[0]):
        for x in range(game.board.shape[1]):
            val = game.board[IntVector2(x,y)]
            if val >= 0:
                counts[int(val)] += 1
                if counts[int(val)] > 1:
                    #game.printGame()
                    return True
    return False


class DepthSaver:
    def __init__(self, cannon, bredthLimit=None):
        self.memo = set()
        self.exploredAtDepth = set()
        self.depthToExplore = 0
        self.cannon = cannon

        self.hashes = []
        self.solutions = []

        self.bredthLimit = bredthLimit
        self.bredthCounter = []

        # ================ single look stuff ===================
        self.boardToView = 3
        self.depthToView = 3
        self.doneViewing = False
        self.shouldView = False

        self.viewPieceMemo = set() # memoizes where pieces have already been printed
        # ======================================================

    # Explore and save to memory the boards at a given number of pieces placed
    def exploreDepth(self, depth, game=None):
        self.memo = set()
        self.exploredAtDepth = set()
        self.depthToExplore = depth
        if self.bredthLimit is not None:
            self.bredthCounter = [0] * (depth + 1)

        if game is None:
            game = QuartoGame(twistCount=1, verbose=False, undoMemLength=0)
        startTime = time.time()
        self._explore(game, 0, False)
        print(f'Found {len(self.exploredAtDepth)} boards with {depth} pieces on them in {(time.time() - startTime) :.03f}')

    # recursive explore function
    def _explore(self, game: QuartoGame, depth: int, placingPiece: bool):
        if self.bredthLimit is not None:
            if self.bredthCounter[depth] >= self.bredthLimit:
                return
            if not placingPiece:
                self.bredthCounter[depth] += 1

        if len(self.memo) % 10_000 == 0:
            print(f'Found a total of {len(self.exploredAtDepth)}', end='\r')


        if placingPiece:
            gameHash = game.hashBoard()
            piece = game.getSelectedPieces()[0]
            
            if (gameHash, piece) in self.memo:
                return
            self.memo.add((gameHash, piece))
            for place in game.getAvaliableSquares():
                game.placePiece(piece, place)
                self._explore(game, depth+1, False)
                game.removePiece(place)
        else:
            game = self.cannon.cannonizeGame(game)

            gameHash = game.hashBoard()
            if (gameHash, None) in self.memo:
                return

            self.memo.add((gameHash, None))
            if depth == self.depthToExplore:
                if not game.checkWinFull():
                    self.exploredAtDepth.add(gameHash)
                return
            if depth >= 4 and game.checkWinFull():
                return

            # print(f"//////////////////////// Placeing {game.getRemainingPieces()} ///////////////////////////")
            # print(game.placedPieces)
            # game.printGame()
            # print("//////////////////////////////////////////////////////////////////////////////")
            for piece in game.getRemainingPieces():
                game.selectPiece(piece)
                self._explore(game, depth, True)
                game.deselectAll()

    # Stores the explored states as hash solution pairs, with the default '-' to represent 
    # that no solution has been found yet
    def saveDepth(self, fileName, path="depthTables/"):
        with open(path + fileName, 'w') as f:
            for key in self.exploredAtDepth:
                f.write(str(key))
                f.write(',')
                f.write('-') # No solution for this value
                f.write('\n')

    # Turns an input hash string into a useable form
    def processInputHash(self, inputHash):
        return int(inputHash)
    
    # Turns an input solution into a useable form
    def processInputSol(self, inputSol):
        if inputSol == '-':
            return None
        # TODO convert solution string into an actual usable solution
        return inputSol

    # Loads a game depth stored as hash solution pairs into memory
    def loadGames(self, fileName, path="depthTables/"):
        self.hashes = []
        self.solutions = []

        with open(path + fileName) as f:
            fileString = f.read()
            hashSolPairs = fileString.split('\n')
            
            for hashSolPair in hashSolPairs:
                splitPair = hashSolPair.split(',')
                if len(splitPair) == 2: # Extrenuous new lines will not be of length 2
                    self.hashes.append(self.processInputHash(splitPair[0]))
                    self.solutions.append(self.processInputSol(splitPair[1]))

    # Saves the hash, solution pairs at a given destination
    def saveSolution(self, fileName, path="depthTables/"):
        with open(path + fileName, 'w') as f:
            for i in range(len(self.hashes)):
                f.write(str(self.hashes[i]))
                f.write(',')
                if len(self.solutions) <= i or self.solutions[i] is None:
                    f.write('-')
                else:
                    f.write(self.solutions[i])
                f.write('\n')

    # Returns the game at a given index
    def getGame(self, index, isAffine=False):
        if isAffine:
            game = Affine4Game()
        else:
            game = QuartoGame()
        game.loadFromHash(self.hashes[index])
        return game
    
    # Set the solution of a current index
    # Currently a simple assignment, could involve processing later
    def setSolution(self, index, sol):
        self.solutions[index] = sol


# saver = DepthSaver(Affine4Cannon())

# saver.exploreDepth(7, Affine4Game(undoMemLength=0))

# saver.saveDepth("Affine7BoardsSmall.txt")
