import random
from game_logic import CheckersGame

class RandomBot:
    """A bot that selects random valid moves."""

    def __init__(self, player_color: str):
        self.player_color = player_color

    def select_move(self, game: CheckersGame):
        """Selects a random valid move for the bot."""
        game.calculate_current_valid_moves()
        if not game.valid_moves:
            print("No valid moves available.")
            return None

        # Select a move at random from the valid moves
        move = random.choice(game.valid_moves)
        return move


class QuantumBot:
    """A bot that uses quantum principles to select moves."""

    def __init__(self, player_color: str):
        self.player_color = player_color

    def select_move(self, game: CheckersGame):
        """Selects a move based on simulated quantum logic."""
        game.calculate_current_valid_moves()
        if not game.valid_moves:
            print("No valid moves available.")
            return None

        # Use a weighted random selection based on move quality
        move_weights = [(move, self.evaluate_move(move, game)) for move in game.valid_moves]
        total_weight = sum(weight for _, weight in move_weights)

        if total_weight == 0:
            return random.choice(game.valid_moves)  # Fallback to random if no weight

        # Select a move based on weighted probabilities
        random_choice = random.uniform(0, total_weight)
        cumulative_weight = 0

        for move, weight in move_weights:
            cumulative_weight += weight
            if cumulative_weight >= random_choice:
                return move

        return random.choice(game.valid_moves)  # Fallback

    def evaluate_move(self, move, game: CheckersGame):
        """Evaluate the quality of a move based on various criteria."""
        row_start, col_start, row_end, col_end = move
        score = 0

        # Increase score for capturing moves
        if abs(row_start - row_end) == 2:
            score += 10  # Prioritize capturing

        # Encourage moving towards the center of the board
        center_positions = [(3, 3), (3, 4), (4, 3), (4, 4)]
        if (row_end, col_end) in center_positions:
            score += 5

        # Encourage piece safety (not leaving pieces vulnerable)
        if game.board[row_start][col_start] == self.player_color:
            if row_end > 0 and game.board[row_end - 1][col_end] != ' ':
                score -= 2  # Penalize moves that leave pieces vulnerable

        # Encourage keeping pieces on the board (not losing pieces)
        if game.board[row_end][col_end] == ' ':
            score += 1  # Score for moving to an empty space

        return score
