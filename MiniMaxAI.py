from QuartoGame import QuartoGame
from QuartoDataTypes import IntVector2
import math
import random

"""
MiniMaxAI class implements the minimax algorithm with alpha-beta pruning to play Quarto.
It uses transposition tables to avoid redundant calculations and supports randomized selection
among equally good moves to enable unique gameplay.
"""
class MiniMaxAI:
    
    """
    Initializes the MiniMaxAI object with a transposition table and search depth.
    """
    def __init__(self):
        self.transposition_table = {}
                        # Be careful with this number (Higher = Slower & theoretically more advanced)
        self.depth = 3  # Controls how deep minimax will search


    """
    placePiece()
        Determines and places the best piece (provided by the opponent) on the game board.
        This method calls minimax() to search for the optimal placement.

        Parameters:
        game (QuartoGame): The current state of the game.
    """
    def placePiece(self, game: QuartoGame) -> None:
        current_piece = game.getSelectedPieces()[0] 
        _, best_square, _ = self.minimax(game.copy(), self.depth, alpha=-math.inf, beta=math.inf, maximizing=True, current_piece=current_piece)
        if best_square is not None:
            game.placePiece(current_piece, best_square)


    """
    choosePiece()
        Chooses the next piece to give to the opponent. Uses minimax() to determine which piece
        gives the opponent the least advantage.

        Parameters:
        game (QuartoGame): The current state of the game.
    """
    def choosePiece(self, game: QuartoGame) -> None:
        _, _, best_piece = self.minimax(game.copy(), self.depth, alpha=-math.inf, beta=math.inf, maximizing=False, current_piece=None)
        if best_piece is not None:
            game.selectPiece(best_piece)


    """
    minimax()
        Implements the Minimax algorithm with Alpha-Beta pruning to evaluate all possible game states
        and determine the best move or piece selection.

        Uses transposition tables to avoid redundant calculations.

        Parameters:
        game (QuartoGame): The current state of the game.
        depth (int): The current search depth.
        alpha (float): Best guaranteed score for the maximizer.
        beta (float): Best guaranteed score for the minimizer.
        maximizing (bool): True if the AI is maximizing its advantage, False if minimizing.
        current_piece (int): The piece to place (or None when choosing a piece for the opponent).

        Returns:
        tuple: (best_score, best_square, best_piece)
    """
    def minimax(self, game: QuartoGame, depth: int, alpha: float, beta: float, maximizing: bool, current_piece: int):
        game_hash = (game.hashBoard(), tuple(game.getSelectedPieces()), current_piece, maximizing)

        # If this state has already been evaluated, return cached result
        if game_hash in self.transposition_table:
            return self.transposition_table[game_hash]
        
        # Base case: If depth is 0, game is won, or board is full, return evaluation score
        if depth == 0 or game.checkWin() or len(game.getAvaliableSquares()) == 0:
            return self.evaluate(game), None, None

        if maximizing:
            best_score = -math.inf # Initialize best score for maximizer
            best_squares = [] # Track equally good moves

            for square in game.getAvaliableSquares():
                g = game.copy()
                g.placePiece(current_piece, square) # Simulate placing the piece

                if g.checkWin():
                    return 100 - (self.depth - depth), square, None

                eval, best_piece = self.minimize_piece_selection(g, depth, alpha, beta)
                if eval > best_score:
                    best_score = eval
                    best_squares = [square]
                elif eval == best_score:
                    best_squares.append(square)

                alpha = max(alpha, eval) # Update alpha for alpha-beta pruning
                if beta <= alpha:
                    break # Beta cutoff (prune remaining branches)

            best_square = random.choice(best_squares) if best_squares else random.choice(game.getAvaliableSquares())
            self.transposition_table[game_hash] = (best_score, best_square, None)
            return best_score, best_square, None

        else:
            best_score = math.inf # Initialize best score for minimizer (opponent)
            best_pieces = [] # Track equally good piece selections

            for piece in game.getRemainingPieces():
                g = game.copy()
                g.selectPiece(piece) # Simulate giving this piece to the opponent
                eval, best_square, _ = self.minimax(g, depth - 1, alpha, beta, maximizing=True, current_piece=piece)

                if eval < best_score:
                    best_score = eval
                    best_pieces = [piece]
                elif eval == best_score:
                    best_pieces.append(piece)

                beta = min(beta, eval) # Update beta for pruning
                if beta <= alpha:
                    break # Alpha cutoff (prune remaining branches)

            best_piece = random.choice(best_pieces) if best_pieces else random.choice(game.getRemainingPieces())
            self.transposition_table[game_hash] = (best_score, None, best_piece)
            return best_score, None, best_piece


    """
    minimize_piece_selection()
        Determines the best piece to give to the opponent by evaluating all possible selections
        with the minimax algorithm. This is called when the AI places a piece and chooses
        the next piece for the opponent.

        Parameters:
        game (QuartoGame): The current state of the game.
        depth (int): The current search depth.
        alpha (float): Best guaranteed score for the maximizer.
        beta (float): Best guaranteed score for the minimizer.

        Returns:
        tuple: (best_score, None, best_piece)
    """
    def minimize_piece_selection(self, game: QuartoGame, depth: int, alpha: float, beta: float):
        if len(game.getRemainingPieces()) == 0:
            return 0, None  # Safe exit on stalemate
    
        best_score = math.inf
        best_pieces = []

        for piece in game.getRemainingPieces():
            g = game.copy()
            g.selectPiece(piece)
            eval, _, _ = self.minimax(g, depth - 1, alpha, beta, maximizing=True, current_piece=piece)

            if eval < best_score:
                best_score = eval
                best_pieces = [piece]
            elif eval == best_score:
                best_pieces.append(piece)

            beta = min(beta, eval)
            if beta <= alpha:
                break

        best_piece = random.choice(best_pieces) if best_pieces else random.choice(game.getRemainingPieces())
        return best_score, best_piece


    """
    evaluate()
        Assigns a heuristic score to the current game state based on potential threats,
        completed lines, and matching traits.

        Parameters:
        game (QuartoGame): The current state of the game.

        Returns:
        float: Evaluation score for the current game state.
    """
    def evaluate(self, game: QuartoGame) -> float:
        if game.checkWin():
            return 100 

        score = 0
        for line in self.get_all_lines(game):
            ai_count, opp_count, empty_count, shared_bits = self.analyze_line_with_traits(game, line)
            if ai_count == 3 and empty_count == 1:
                score += 50 # Strong winning potential
            elif opp_count == 3 and empty_count == 1:
                score -= 50 # High-risk losing scenario
            elif ai_count == 2 and empty_count == 2:
                score += 10 + shared_bits # Favorable progression
            elif opp_count == 2 and empty_count == 2:
                score -= 10 + shared_bits # Block potential threats

        return score


    """
    get_all_lines()
        Returns a list of all rows, columns, and diagonals on the game board.

        Parameters:
        game (QuartoGame): The current state of the game.

        Returns:
        list: List of lists of IntVector2 representing all lines on the board.
    """
    def get_all_lines(self, game: QuartoGame):
        lines = []
        size = game.dims.x

        for i in range(size):
            row = [IntVector2(i, j) for j in range(size)]
            col = [IntVector2(j, i) for j in range(size)]
            lines.append(row)
            lines.append(col)

        diag1 = [IntVector2(i, i) for i in range(size)]
        diag2 = [IntVector2(i, size - i - 1) for i in range(size)]
        lines.append(diag1)
        lines.append(diag2)

        return lines


    """
    analyze_line_with_traits()
        Analyzes a line (row, column, diagonal) to count AI and opponent pieces,
        empty spots, and matching traits across placed pieces.

        Parameters:
        game (QuartoGame): The current state of the game.
        line (list[IntVector2]): A list of positions in the line.

        Returns:
        tuple: (ai_count, opp_count, empty_count, shared_bits)
    """
    def analyze_line_with_traits(self, game: QuartoGame, line: list[IntVector2]):
        ai_count = 0
        opp_count = 0
        empty_count = 0
        shared_bits = 0

        traits = None
        for pos in line:
            piece = int(game.board[pos.x, pos.y])
            if piece < 0:
                empty_count += 1
            elif piece in game.getSelectedPieces():
                ai_count += 1
                traits = piece if traits is None else traits & piece
            else:
                opp_count += 1
                traits = piece if traits is None else traits & piece

        if traits is not None:
            shared_bits = bin(traits).count('1')

        return ai_count, opp_count, empty_count, shared_bits
