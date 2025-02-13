from QuartoGame import QuartoGame


# An object for converting quarto games into cannonical form
#
#   "I'm not in the habit of hunting rabbits with a cannon; 
#    but I will use one to solve Quarto" - Hawkeye Mihawk
#
class QuartoCannon:
    def __init__(self):
        pass

# Takes a QuartoGame as input, returns the cannonical form of that game
# It should probably return a copy, rather than modify it in place
# But we can figure that out later
    def cannonizeGame(self, game:QuartoGame) -> QuartoGame:
        return game.copy()

# Reload the QuartoCannon. In case game specific data is being stored,
# we can reset it here before a new game is started.
    def reset(self):
        pass

