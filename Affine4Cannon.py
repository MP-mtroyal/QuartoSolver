from QuartoDataTypes import IntVector2
from QuartoCannon import QuartoCannon
from Affine4Game import Affine4Game
from QuartoGame import QuartoGame
from GreatQuartoCannon import GreatQuartoCannon

class Affine4Cannon(QuartoCannon):
    def __init__(self):
        super().__init__()

        self.baseCannon = GreatQuartoCannon()

        # Hard coded indices for faster cannonization
        self.tripleChainIndices = [
            IntVector2(0, 0),
            IntVector2(1, 0),
            IntVector2(2, 0),
            IntVector2(2, 1),
            IntVector2(2, 2),
            IntVector2(1, 1),
        ]

    def cannonizeGame(self, game: Affine4Game):
        placedPieces = game.getPlacedPieces()

        if len(placedPieces) == 0:
            pass
        elif len(placedPieces) == 1:
            game = self.singlePieceBoard()
        elif len(placedPieces) == 2:
            game = self.twoPieceBoard(placedPieces)
        elif len(placedPieces) == 3:
            game = self.threePieceBoard(game, placedPieces)
        elif len(placedPieces) == 4:
            basicCannon = self.fourPieceBoard(game, placedPieces)
            game = self.baseCannon.cannonizeGame(basicCannon)
        elif len(placedPieces) == 5:
            game = self.fivePieceBoard(game, placedPieces)
            #game = self.baseCannon.cannonizeGame(basicCannon)
        elif len(placedPieces) == 6:
            game = self.sixPieceBoard(game, placedPieces)
            game = self.baseCannon.cannonizeGame(game)
        else:
            game = self.baseCannon.cannonizeGame(game)

        return game

    def traitsInCommon(self, p1, p2):
        commonTraits = bin(p1 & p2).count('1')
        commonTraits += bin((p1 ^ 15) & (p2 ^ 15)).count('1')
        return commonTraits
    
    def bestPiece(self, game: Affine4Game, placed, toPlace):
        for i in range(toPlace):
            if game.remainingPieces[i] < 1:
                continue
            for n in range(len(placed)):
                # Don't check againt the src piece
                if placed[n] == toPlace:
                    continue
                # End loop early if current pieces shares a different number of traits
                # in common with the placed piece
                if self.traitsInCommon(i, placed[n]) != self.traitsInCommon(toPlace, placed[n]):
                    break
            # If the loop didn't end early, return the current piece
            else:
                return i
        
        return toPlace

    def singlePieceBoard(self):
        newGame = Affine4Game()
        newGame.selectPiece(0)
        newGame.placePiece(0, IntVector2(0,0))
        return newGame
    
    def twoPieceBoard(self, placedPieces):
        newGame = self.singlePieceBoard()
        newPiece = self.bestPiece(newGame, placedPieces, placedPieces[-1])
        newGame.selectPiece(newPiece)
        newGame.placePiece(newPiece, IntVector2(1,0))
        return newGame
    
    def threePieceBoard(self, game: Affine4Game, placedPieces):
        newGame = Affine4Game()

        # Find how many pieces are in a line
        commonLines = game.getCommonLines()
        longestLine = 0
        for i in range(len(commonLines)):
            longestLine = max(len(commonLines[i]), longestLine)

        #newPiece = self.bestPiece(newGame, placedPieces, placedPieces[-1])
        placedPieces[-1] = self.bestPiece(newGame, placedPieces, placedPieces[-1])
        placedPieces.sort()

        indices = [IntVector2(0,0), IntVector2(1,0)]
        indices += [IntVector2(2,0)] if longestLine == 3 else [IntVector2(2,1)]

        for i in range(len(placedPieces)):
            newGame.selectPiece(placedPieces[i])
            newGame.placePiece(placedPieces[i], indices[i])

        return newGame
    
    def fourPieceBoard(self, game: Affine4Game, placedPieces):
        newGame = Affine4Game()

        commonLines = game.getCommonLines()
        longestLine = []
        for i in range(len(commonLines)):
            if len(commonLines[i]) > len(longestLine):
                longestLine = commonLines[i]
        
        bestPiece = self.bestPiece(game, placedPieces, placedPieces[-1])
        if bestPiece not in placedPieces: # New best piece found
            if placedPieces[-1] in longestLine: # Best piece replaces one in longest line
                longestLine[longestLine.index(placedPieces[-1])] = bestPiece
        placedPieces[-1] = bestPiece

        longestLine.sort()
        for i in range(len(longestLine)):
            newGame.selectPiece(longestLine[i])
            newGame.placePiece(longestLine[i], IntVector2(i, 0))

        if len(longestLine) == 3:
            newPlaced = newGame.getPlacedPieces()
            for piece in placedPieces:
                if piece not in newPlaced:
                    newGame.selectPiece(piece)
                    newGame.placePiece(piece, IntVector2(0, 1))
                    break
        elif len(longestLine) == 2:
            newPlaced = newGame.getPlacedPieces()
            placement = 0
            for piece in range(16): # loop through all 16 in order to force implicit sorting
                if piece in placedPieces and piece not in newPlaced:
                    newGame.selectPiece(piece)
                    newGame.placePiece(piece, IntVector2(placement, 1))
                    placement += 1
                    if placement >= 2:
                        break

        return newGame
    
    def fivePieceBoard(self, game: Affine4Game, placedPieces):
        newGame = Affine4Game()

        commonLines = game.getCommonLines()
        longestLine = []
        lineCounts = [0] * 5 # how many of each length common line are present
        length3Lines = [] # Used in boards with 2 length 3s
        
        for i in range(len(commonLines)):
            if len(commonLines[i]) > len(longestLine):
                longestLine = commonLines[i]
            if len(commonLines[i]) == 3:
                length3Lines.append(commonLines[i])
            lineCounts[len(commonLines[i])] += 1

        bestPiece = self.bestPiece(game, placedPieces, placedPieces[-1])
        if bestPiece not in placedPieces: # New best piece found
            if placedPieces[-1] in longestLine: # Best piece replaces one in longest line
                longestLine[longestLine.index(placedPieces[-1])] = bestPiece
            for line in length3Lines:
                if placedPieces[-1] in line:
                    line[line.index(placedPieces[-1])] = bestPiece
        placedPieces[-1] = bestPiece
        longestLine.sort()

        for i in range(len(longestLine)):
            newGame.selectPiece(longestLine[i])
            newGame.placePiece(longestLine[i], IntVector2(i, 0))

        if lineCounts[3] == 2:
            newPlaced = newGame.getPlacedPieces()
            commonPiece = None
            for piece in length3Lines[0]:
                if piece in length3Lines[1]:
                    commonPiece = piece
                    break

            if longestLine.index(commonPiece) != 0:
                replaceIndex = longestLine.index(commonPiece)
                newGame.swapPieces(IntVector2(0,0), IntVector2(replaceIndex, 0))

            xIndex = 0 #longestLine.index(commonPiece)
            placement = 1

            for piece in range(16): # loop through all 16 in order to force implicit sorting
                if piece in placedPieces and piece not in newPlaced:
                    newGame.selectPiece(piece)
                    newGame.placePiece(piece, IntVector2(xIndex, placement))
                    placement += 1
                    if placement >= 3:
                        break
        
        else:
            newPlaced = newGame.getPlacedPieces()
            placement = 0
            for piece in range(16): # loop through all 16 in order to force implicit sorting
                if piece in placedPieces and piece not in newPlaced:
                    newGame.selectPiece(piece)
                    newGame.placePiece(piece, IntVector2(placement, 1))
                    placement += 1
                    if placement >= 2 or lineCounts[4] > 0:
                        break
        
        return newGame

    class chainNode:
        def __init__(self, val):
            self.val = val
            self.next = None
            self.prev = None

    def getTripleChain(self, tripleArrays):
        assert len(tripleArrays) == 3
        assert len(tripleArrays[0]) == 3
        heads = []
        for i in range(len(tripleArrays)):
            for j in range(len(tripleArrays)):
                for n in range(len(tripleArrays)): # O(n^3) yuck. but n is always 3
                    if i != n and tripleArrays[i][j] in tripleArrays[n]:
                        if tripleArrays[i][j] not in heads:
                            heads.append(tripleArrays[i][j])

        heads.sort()
        currArr = None
        for i in range(len(tripleArrays)):
            if heads[0] in tripleArrays[i] and heads[1] in tripleArrays[i]:
                currArr = tripleArrays[i]
                tripleArrays = tripleArrays[:i] + tripleArrays[i+1:]
                break
        
        chain = [heads[0]]
        for i in range(len(currArr)):
            if currArr[i] != heads[0] and currArr[i] != heads[1]:
                chain.append(currArr[i])
                break
        
        chain.append(heads[1])
        for i in range(len(tripleArrays)):
            if heads[1] in tripleArrays[i] and heads[2] in tripleArrays[i]:
                currArr = tripleArrays[i]
                tripleArrays = tripleArrays[:i] + tripleArrays[i+1:]
                break
        
        for i in range(len(currArr)):
            if currArr[i] != heads[1] and currArr[i] != heads[2]:
                chain.append(currArr[i])
                break
        
        chain.append(heads[2])
        currArr = tripleArrays[0]
        for i in range(len(currArr)):
            if currArr[i] != heads[2] and currArr[i] != heads[0]:
                chain.append(currArr[i])
                break
        
        return chain


    def sixPieceBoard(self, game:Affine4Game, placedPieces):
        commonLines = game.getCommonLines()
        longestLine = []
        lineCounts = [0] * 6 # how many of each length common line are present
        length3Lines = [] # Used in boards with 2 length 3s
        
        for i in range(len(commonLines)):
            if len(commonLines[i]) > len(longestLine):
                longestLine = commonLines[i]
            if len(commonLines[i]) == 3:
                length3Lines.append(commonLines[i])
            lineCounts[len(commonLines[i])] += 1

        if lineCounts[3] == 4:
            return game.copy() # there is only 1 possible board with 4 lines of 3

        newGame = Affine4Game()

        bestPiece = self.bestPiece(game, placedPieces, placedPieces[-1])
        if bestPiece not in placedPieces: # New best piece found
            if placedPieces[-1] in longestLine: # Best piece replaces one in longest line
                longestLine[longestLine.index(placedPieces[-1])] = bestPiece
            for line in length3Lines:
                if placedPieces[-1] in line:
                    line[line.index(placedPieces[-1])] = bestPiece
        placedPieces[-1] = bestPiece

        if lineCounts[3] == 3:
            sortedChain = self.getTripleChain(length3Lines)
            for i in range(len(sortedChain)):
                newGame.selectPiece(sortedChain[i])
                newGame.placePiece(sortedChain[i], self.tripleChainIndices[i])
            return newGame

        longestLine.sort()

        for i in range(len(longestLine)):
            newGame.selectPiece(longestLine[i])
            newGame.placePiece(longestLine[i], IntVector2(i, 0))

        if lineCounts[4] == 1:
            offset = None
            if lineCounts[3] == 1:
                commonPiece = None
                for piece in length3Lines[0]:
                    if piece in longestLine:
                        commonPiece = piece
                        break
                if longestLine.index(commonPiece) != 0:
                    replaceIndex = longestLine.index(commonPiece)
                    newGame.swapPieces(IntVector2(0,0), IntVector2(replaceIndex, 0))
                offset = IntVector2(0, 1) # populate downwards
            else:
                offset = IntVector2(1, 0) # populate rightwards

            placement = IntVector2(0, 1)
            for piece in range(16):
                if piece not in longestLine:
                    if piece in placedPieces:
                        newGame.selectPiece(piece)
                        newGame.placePiece(piece, placement)
                        placement = IntVector2(placement.x + offset.x, placement.y + offset.y)
                        if placement.x + placement.y >= 3:
                            break

        else: # 2 length 3 lines is the only other possibility
            # one case for piece shared between both lines, one for 2 distinct lines
            commonPiece = None
            for piece in length3Lines[0]:
                if piece in length3Lines[1]:
                    commonPiece = piece
                    break
            if commonPiece is None:
                remainingLine = length3Lines[1] if length3Lines[0][0] in longestLine else length3Lines[0]
                remainingLine.sort()
                placement = IntVector2(0, 1)
                for piece in remainingLine:
                    newGame.selectPiece(piece)
                    newGame.placePiece(piece, placement)
                    placement = IntVector2(placement.x + 1, placement.y)
            else:
                if commonPiece != longestLine[0]:
                    replaceIndex = longestLine.index(commonPiece)
                    newGame.swapPieces(IntVector2(0,0), IntVector2(replaceIndex, 0))
                remainingLine = length3Lines[1] if length3Lines[0][0] in longestLine else length3Lines[0]
                placement = IntVector2(0, 1)
                placedPieces.sort()
                #for piece in range(16):
                #print(placedPieces)
                for piece in placedPieces:
                    if piece not in longestLine:
                        if piece in remainingLine:
                            newGame.selectPiece(piece)
                            if not newGame.placePiece(piece, placement):
                                pass
                                # print("--------------------------------------------")
                                # game.printGame()
                                # print()
                                # newGame.printGame()
                            placement = IntVector2(placement.x, placement.y + 1)
                        else: # only occurs for the one piece not in either line of 3
                            newGame.selectPiece(piece)
                            if not newGame.placePiece(piece, IntVector2(1,1)):
                                pass
                                # print("--------------------------------------------")
                                # game.printGame()
                                # print()
                                # newGame.printGame()
        return newGame

# game = Affine4Game()
# cannon = Affine4Cannon()

# game.selectPiece(0)
# game.placePiece(0, IntVector2(0,0))

# game.selectPiece(6)
# game.placePiece(6, IntVector2(1,0))

# game.selectPiece(1)
# game.placePiece(1, IntVector2(2,0))

# game.selectPiece(2)
# game.placePiece(2, IntVector2(0,1))

# game.selectPiece(3)
# game.placePiece(3, IntVector2(0, 2))

# game.selectPiece(4)
# game.placePiece(4, IntVector2(2,1))

# game.printGame()

# game = cannon.cannonizeGame(game)

# game.printGame()