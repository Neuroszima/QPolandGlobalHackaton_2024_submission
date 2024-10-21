try:
    import pygame
except ImportError:
    pygame = None


class CheckersGame:
    STARTING_BOARD = [
        [' ', 'B', ' ', 'B', ' ', 'B', ' ', 'B'],
        ['B', ' ', 'B', ' ', 'B', ' ', 'B', ' '],
        [' ', 'B', ' ', 'B', ' ', 'B', ' ', 'B'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        ['R', ' ', 'R', ' ', 'R', ' ', 'R', ' '],
        [' ', 'R', ' ', 'R', ' ', 'R', ' ', 'R'],
        ['R', ' ', 'R', ' ', 'R', ' ', 'R', ' ']
    ]
    STARTING_PLAYER = "R"
    PLAYER_1_COLOR = "R"
    PLAYER_2_COLOR = "B"
    PLAYER_BOARD_DIRECTION = {
        "R": -1,  # "reducing rownum" -> moving up
        "B": 1  # "increasing rownum" -> moving down
    }

    def __init__(self):
        self.board = self.STARTING_BOARD
        self.current_player = self.STARTING_PLAYER
        self.current_player_direction = self.PLAYER_BOARD_DIRECTION[self.current_player]
        self.valid_moves: list = []

    def human_readable_possible_moves(self) -> list[str]:
        all_moves_printed = []
        for move in self.valid_moves:
            all_moves_printed.append(f"{move[0]}{chr(move[1]+65)} -> {move[2]}{chr(move[3]+65)}")
        return all_moves_printed

    def calculate_current_valid_moves(self):
        """
        Generates a list of valid moves based on the current state of the board.

        :param player_direction: when playing red -> "+1" (moving up), "-1" when black
        """
        valid_moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                if self.board[row][col] == self.current_player:  # Assuming 'R' represents the bot's pieces
                    # Check for valid moves in all possible directions
                    if 0 < row + self.current_player_direction < len(self.board):

                        if (col + 1 < len(self.board[row])) and (
                                self.board[row + self.current_player_direction][col + 1] == ' '):
                            # move towards right, up or down (depending on player)
                            valid_moves.append(
                                (row, col, row + self.current_player_direction, col + 1)
                            )

                        if (col - 1 >= 0) and (self.board[row + self.current_player_direction][col - 1] == ' '):
                            # move towards left, up or down (depending on player)
                            valid_moves.append(
                                (row, col, row + self.current_player_direction, col - 1)
                            )

        self.valid_moves = valid_moves

    def mark_available(self):
        if self.valid_moves:
            for move in self.valid_moves:
                self.board[move[2]][move[3]] = "G"
