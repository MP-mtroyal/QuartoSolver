
from QuartoGame import QuartoGame
from QuartoAI import QuartoAI


#===== Simple AI playing against itself. 
# Just a sanity check for seeing that everything is working.
quit = False
twistCount = 16
while not quit:
    g = QuartoGame(twistCount=twistCount)
    ai = QuartoAI()

    while not g.checkWin() and len(g.getRemainingPieces()) > 0:
        input("\nPress Enter...")
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

    c = input('\nPlay again? y/n  ')
    if c != 'y':
        quit = True



