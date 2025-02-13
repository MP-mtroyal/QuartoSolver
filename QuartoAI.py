from QuartoGame import QuartoGame
from random import choice

# A basic Quarto AI class
class QuartoAI:
    def __init__(self):
        pass
    
    def choosePiece(self, game:QuartoGame) -> None:
        #avoid accidently modifying the src game
        g = game.copy()

        if len(g.getRemainingPieces()) < 1:
            print(f'Error: AI could not choose piece, there are no remaining pieces.')
            return

        avaliableSquares = g.getAvaliableSquares()
        validChoices = []
        for piece in g.getRemainingPieces():
            pieceIsValid = True
            pieceChosen = g.selectPiece(piece)
            if not pieceChosen:
                print(f'Error: AI could not choose piece. Something went REALLY wrong, you should not ever see this.')
                return
            for square in avaliableSquares:
                piecePlaced = g.placePiece(piece, square)
                if not piecePlaced:
                    print(f'Error: AI could not place piece. Something went REALLY wrong, you should not ever see this.')
                    return
                #Piece allows opponent to win
                if g.checkWin(): 
                    pieceIsValid = False
                g.undo()
            g.undo()
            if pieceIsValid:
                validChoices.append(piece)
        pieceToChoose = choice(validChoices) if len(validChoices) > 0 else choice(game.getRemainingPieces())
        game.selectPiece(pieceToChoose)


    def placePiece(self, game:QuartoGame) -> None:
        #avoid accidently modifying the src game
        g = game.copy()
        avaliablePieces  = g.getSelectedPieces()
        avaliableSquares = g.getAvaliableSquares()
        if len(avaliablePieces) < 1 or len(avaliableSquares) < 1:
            print(f'Error: AI cannot place piece.')
            return

        for piece in avaliablePieces:
            for square in avaliableSquares:
                piecePlaced = g.placePiece(piece, square)
                if not piecePlaced:
                    print('Error: AI piece placement failed.')
                    return
                if g.checkWin():
                    #Found a winning move
                    game.placePiece(piece, square)
                    return
                else:
                    g.undo()

        #No winning move found, choose randomly
        piece  = choice(avaliablePieces) if len(avaliablePieces) > 1 else avaliablePieces[0]
        square = choice(avaliableSquares)
        game.placePiece(piece, square)

