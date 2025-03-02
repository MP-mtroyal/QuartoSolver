
from QuartoGame import QuartoGame
from QuartoAI import QuartoAI
from MiniMaxAI import MiniMaxAI
from MiniMaxAI1 import MiniMaxAI1


#===== Simple AI playing against itself. 
# Just a sanity check for seeing that everything is working.
quit = False
twistCount = 1
while not quit:
    g = QuartoGame(twistCount=twistCount)
    g.populateBoard(8)
    #ai = QuartoAI()
    ai = MiniMaxAI1()
    ai.transposition_table.clear()

    while not g.checkWin() and len(g.getRemainingPieces()) > 0 and len(g.getAvaliableSquares()) > 0:
        #input("\nPress Enter...")
        for _ in range(twistCount):
            if len(g.getRemainingPieces()) < 1:
                break
            ai.choosePiece(g)
        ai.placePiece(g)
        g.printGame()
    
    print('\n\n')
    if g.checkWin():
        print('WINNER!')
    else:
        print("Stalemate :(")
    
    print()

    #c = input('\nPlay again? y/n  ')
    #if c != 'y':
    #    quit = True