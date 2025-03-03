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
                        # If using populateBoard(n), depth should be 16-n
        self.depth = 16  # Controls how deep minimax will search


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
        game_hash = (game.hashBoard(), current_piece, maximizing)

        # If this state has already been evaluated, return cached result
        if game_hash in self.transposition_table:
            return self.transposition_table[game_hash]
        
        # Base case: If depth is 0, game is won, board is full, or no pieces remain, return evaluation score
        if depth == 0 or game.checkWin() or len(game.getAvaliableSquares()) == 0 or len(game.getRemainingPieces()) == 0:
            if len(game.getAvaliableSquares()) == 0 and not game.checkWin():
                return 0, None, None  # Stalemate - neutral outcome
            return self.evaluate(game), None, None

        if maximizing:
            best_score = -math.inf # Initialize best score for maximizer
            best_squares = [] # Track equally good moves

            for square in game.getAvaliableSquares():
                g = game.copy()
                g.placePiece(current_piece, square) # Simulate placing the piece

                if g.checkWin():
                    score = self.evaluate(g)
                    self.transposition_table[game_hash] = (score, square, None)
                    return score, square, current_piece

                eval, _, _ = self.minimax(g, depth - 1, alpha, beta, maximizing=False, current_piece=current_piece)
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
                if not self.is_piece_safe(game, piece):
                    continue  # Skip this piece — it's too dangerous
                g = game.copy()
                g.selectPiece(piece) # Simulate giving this piece to the opponent
                eval, _, _ = self.minimax(g, depth - 1, alpha, beta, maximizing=True, current_piece=piece)

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
    is_piece_safe()
        Determines if a given piece is "safe" to hand to the opponent, meaning the piece
        will not immediately complete a winning line for the opponent when placed.

        The safety check works by examining all rows, columns, and diagonals on the board
        and looking for lines with exactly 3 placed pieces and 1 empty square.
        If the given piece would complete all 4 traits in that line (shared_bits == 4), 
        it is considered unsafe.

        Parameters:
        game (QuartoGame): The current state of the game.
        piece (int): The piece to check for safety.

        Returns:
        bool: True if the piece is safe (no immediate win possible), False if the piece 
                would complete a winning line.
    """
    def is_piece_safe(self, game: QuartoGame, piece: int) -> bool:
        for line in self.get_all_lines(game):
            placed_count, empty_count, shared_bits = self.analyze_line_with_traits(game, line)

            if placed_count == 3 and empty_count == 1 and shared_bits == 4:
                return False  # Unsafe - completes a winning line

        return True


    """
    evaluate()
        Evaluates the current state of the game and returns a score for the AI's minimax logic.

        This evaluation is purely based on terminal states (win, loss, or stalemate) and 
        does not assign intermediate heuristic values. This works when the minimax 
        depth is (16) allowing search to the end of the game. Please use populateBoard(n-depth) 
        before running the AI if the search depth is not 16.

        Parameters:
        game (QuartoGame): The current state of the game.
        maximizing (bool): True if the AI is the maximizing player (placing a piece),
                            False if the AI is minimizing (choosing a piece for the opponent).

        Returns:
        float: 1 if the AI wins, -1 if the opponent wins, 0 for a stalemate.
    """
    """
    def evaluate(self, game: QuartoGame, maximizing: bool) -> float:
        if game.checkWin():
            return 1 if maximizing else -1  # AI win if maximizing, AI loss if minimizing

        if len(game.getAvaliableSquares()) == 0:
            return 0  # Stalemate

        return 0  # Non-terminal states are neutral
    """


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
            return 100  # Immediate win check

        score = 0

        for line in self.get_all_lines(game):
            placed_count, empty_count, shared_bits = self.analyze_line_with_traits(game, line)

            if placed_count == 3 and empty_count == 1:
                score += 20 * shared_bits  # Close to win
            elif placed_count == 2 and empty_count == 2:
                score += 5 * shared_bits  # Mid-game heat
            elif placed_count == 1 and empty_count == 3:
                score += 2  # Early-game heat

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
        placed_count = 0
        empty_count = 0
        shared_bits = 0  # How many traits are fully shared across all placed pieces

        # Track both "all zeros" and "all ones" for each bit position
        all_ones = 0b1111   # Start by assuming all bits could be all 1s
        all_zeros = 0b1111  # Start by assuming all bits could be all 0s

        for pos in line:
            piece = int(game.board[pos.x, pos.y])

            if piece < 0:
                empty_count += 1
            else:
                placed_count += 1
                # For each bit position, clear it if the piece breaks the consensus
                all_ones &= piece       # Keeps 1s where all pieces have 1
                all_zeros &= ~piece     # Keeps 1s where all pieces have 0

        # Each bit position that still has a 1 in either all_ones or all_zeros is a shared feature.
        shared_bits = bin(all_ones | all_zeros).count('1')

        return placed_count, empty_count, shared_bits