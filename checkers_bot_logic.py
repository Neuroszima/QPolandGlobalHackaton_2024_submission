import random


def quantum_decision(board: list[list], player_color: str, player_direction: int):
    """
    Randomly selects a valid move from the available moves.
    This is a placeholder for integrating Grover's algorithm.
    """
    valid_moves = get_valid_moves(board, player_color, player_direction)
    if not valid_moves:
        return None  # No valid moves available
    return random.choice(valid_moves)


def get_valid_moves(board: list[list], player_color: str, player_direction: int):
    """
    Generates a list of valid moves based on the current state of the board.

    :param player_direction: when playing red -> "+1" (moving up), "-1" when black
    """
    valid_moves = []
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == player_color:  # Assuming 'R' represents the bot's pieces
                # Check for valid moves in all possible directions
                if 0 < row + player_direction < len(board):
                    if (col + 1 < len(board[row])) and (board[row + player_direction][col + 1] == ' '):
                        valid_moves.append((row, col, row + player_direction, col + 1))
                    if (col - 1 >= 0) and (board[row + player_direction][col - 1] == ' '):
                        valid_moves.append((row, col, row + player_direction, col - 1))
    # print(valid_moves)
    return valid_moves
