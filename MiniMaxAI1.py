from QuartoGame import QuartoGame
from QuartoDataTypes import IntVector2
import math
import random

"""
MiniMaxAI class implements the minimax algorithm with alpha-beta pruning to play Quarto.
It uses transposition tables to avoid redundant calculations and supports randomized selection
among equally good moves to enable unique gameplay.
"""
class MiniMaxAI1:
    
    """
    Initializes the MiniMaxAI object with a transposition table and search depth.
    """
    def __init__(self):
        self.transposition_table = {}
                        # Be careful with this number (Higher = Slower & theoretically more advanced)
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

        if game_hash in self.transposition_table:
            return self.transposition_table[game_hash]

        if depth == 0 or game.checkWin() or len(game.getAvaliableSquares()) == 0 or len(game.getRemainingPieces()) == 0:
            score = self.evaluate(game, maximizing)
            return score, None, None

        if maximizing:
            scores = []
            moves = []

            for square in game.getAvaliableSquares():
                next_game = game.copy()
                next_game.placePiece(current_piece, square)

                if next_game.checkWin():
                    score = self.evaluate(next_game, maximizing=True)
                    scores.append(score)
                    moves.append((square, None))
                    continue

                score, _, _ = self.minimax(next_game, depth-1, alpha, beta, maximizing=False, current_piece=None)
                scores.append(score)
                moves.append((square, None))

                alpha = max(alpha, score)
                if beta <= alpha:
                    break  # Alpha-beta pruning

            if not scores:
                return 0, None, None  # No moves available, should never happen here

            score = sum(scores)
            best_move = moves[scores.index(max(scores))]  # Traditional best move for safety
            self.transposition_table[game_hash] = (score, best_move[0], None)
            return score, best_move, None

        else:
            scores = []
            pieces = []

            for piece in game.getRemainingPieces():
                next_game = game.copy()
                next_game.selectPiece(piece)

                # Defensive check — does this piece give the opponent an immediate threat?
                threat_penalty = self.assess_piece_threat(next_game, piece)

                score, _, _ = self.minimax(next_game, depth-1, alpha, beta, maximizing=True, current_piece=piece)
                adjusted_score = score + threat_penalty
                scores.append(adjusted_score)
                pieces.append(piece)

                beta = min(beta, score)
                if beta <= alpha:
                    break  # Alpha-beta pruning

            if not scores:
                return 0, None, None  # No pieces left, should never happen here

            score = sum(scores)
            best_piece = pieces[scores.index(min(scores))]  # Traditional best piece for safety
            self.transposition_table[game_hash] = (score, None, best_piece)
            return score, None, best_piece



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
    def evaluate(self, game: QuartoGame, maximizing: bool) -> float:
        if game.checkWin():
            return 1 if maximizing else -1  # AI win if maximizing, AI loss if minimizing

        if len(game.getAvaliableSquares()) == 0:
            return 0.1  # Stalemate, give score boost as stalemate is better than losing

        return 0  # Non-terminal states are neutral
    

    def assess_piece_threat(self, game: QuartoGame, piece: int) -> float:
        """
        Check if the selected piece immediately creates a threat (three-in-a-row with matching traits).
        Penalize if so.
        """
        threat_penalty = 0

        for square in game.getAvaliableSquares():
            temp_game = game.copy()
            temp_game.placePiece(piece, square)

            if temp_game.checkWin():
                threat_penalty -= 0.5  # Moderate penalty for handing over a piece that gives a forced win

            if self.creates_three_in_a_row(temp_game, square):
                threat_penalty -= 0.2  # Smaller penalty for creating a threat

        return threat_penalty


    def creates_three_in_a_row(self, game: QuartoGame, square: IntVector2) -> bool:
        """
        Detect if placing at this square would create a three-in-a-row with strong trait overlap.
        """
        lines = self.get_all_lines(game)
        for line in lines:
            if square not in line:
                continue

            placed_count, _, shared_traits = self.analyze_line_with_traits(game, line)

            if placed_count == 3 and shared_traits >= 3:
                return True

        return False

    
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
