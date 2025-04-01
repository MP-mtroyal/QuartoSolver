from QuartoDataTypes import IntVector2
from QuartoCannon import QuartoCannon
from Affine4Game import Affine4Game
from QuartoGame import QuartoGame
from GreatQuartoCannon import GreatQuartoCannon

class Affine4Cannon(QuartoCannon):
    def __init__(self):
        super().__init__()

        self.baseCannon = GreatQuartoCannon()

    def cannonizeGame(self, game: Affine4Game):
        placedPieces = game.getPlacedPieces()

        if len(placedPieces) == 0:
            return game
        elif len(placedPieces) == 1:
            return self.singlePieceBoard()
        elif len(placedPieces) == 2:
            return self.twoPieceBoard(placedPieces)
        elif len(placedPieces) == 3:
            return self.threePieceBoard(game, placedPieces)
        elif len(placedPieces) == 4:
            basicCannon = self.fourPieceBoard(game, placedPieces)
            game = self.baseCannon.cannonizeGame(basicCannon)
            return game

        game = self.baseCannon.cannonizeGame(game)

        return game

    def singlePieceBoard(self):
        newGame = Affine4Game()
        newGame.selectPiece(0)
        newGame.placePiece(0, IntVector2(0,0))
        return newGame
    
    def twoPieceBoard(self, placedPieces):
        newGame = self.singlePieceBoard()
        onesCount = bin(placedPieces[-1]).count('1')
        shiftedPiece = 0
        for i in range(onesCount):
            shiftedPiece += 2 ** i
        newGame.selectPiece(shiftedPiece)
        newGame.placePiece(shiftedPiece, IntVector2(1,0))
        return newGame
    
    def threePieceBoard(self, game: Affine4Game, placedPieces):
        placedPieces.sort()
        newGame = self.twoPieceBoard(placedPieces[:2])

        # Find how many pieces are in a line
        commonLines = game.getCommonLines()
        longestLine = 0
        for i in range(len(commonLines)):
            longestLine = max(len(commonLines[i]), longestLine)
        index = IntVector2(2, 0) if longestLine> 2 else IntVector2(2,1)

        newPiece = placedPieces[-1]
        newGame.selectPiece(newPiece)
        newGame.placePiece(newPiece, index)
        return newGame
    
    def fourPieceBoard(self, game: Affine4Game, placedPieces):
        newGame = Affine4Game()

        commonLines = game.getCommonLines()
        longestLine = []
        for i in range(len(commonLines)):
            if len(commonLines[i]) > len(longestLine):
                longestLine = commonLines[i]
        
        longestLine.sort()
        for i in range(len(longestLine)):
            newGame.selectPiece(longestLine[i])
            newGame.placePiece(longestLine[i], IntVector2(i, 0))

        if len(longestLine) == 3:
            placedPieces = newGame.getPlacedPieces()
            allPlacedPieces = game.getPlacedPieces()
            for piece in allPlacedPieces:
                if piece not in placedPieces:
                    newGame.selectPiece(piece)
                    newGame.placePiece(piece, IntVector2(0, 1))
                    break
        else:
            placedPieces = newGame.getPlacedPieces()
            allPlacedPieces = game.getPlacedPieces()
            placement = 0
            for piece in allPlacedPieces:
                if piece not in placedPieces:
                    newGame.selectPiece(piece)
                    newGame.placePiece(piece, IntVector2(placement, 1))
                    placement += 1
                    if placement >= 2:
                        break

        return newGame


# game = Affine4Game()
# cannon = Affine4Cannon()

# game.printGame()

# game.selectPiece(9)
# game.placePiece(9, IntVector2(3, 1))

# game.printGame()
# game = cannon.cannonizeGame(game)
# game.printGame()

# game.selectPiece(10)
# game.placePiece(10, IntVector2(3, 1))

# game.printGame()
# game = cannon.cannonizeGame(game)
# game.printGame()

# game.selectPiece(10)
# game.placePiece(10, IntVector2(2, 0))

# game.printGame()
# game = cannon.cannonizeGame(game)
# game.printGame()

# a = [0, 7, 2]
# print(a)
# a.sort()
# print(a)