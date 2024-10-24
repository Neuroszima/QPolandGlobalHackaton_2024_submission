# game_logic.py

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
    STARTING_ENEMY = "B"
    PLAYER_1_COLOR = "R"
    PLAYER_2_COLOR = "B"
    PLAYER_BOARD_DIRECTION = {
        "R": -1,  # Red moves up
        "B": 1    # Black moves down
    }

    def __init__(self):
        self.board = self.STARTING_BOARD
        self.current_player = self.STARTING_PLAYER
        self.current_enemy_player = self.STARTING_ENEMY
        self.current_player_direction = self.PLAYER_BOARD_DIRECTION[self.current_player]
        self.valid_moves: list = []
        self.calculate_current_valid_moves()

    def human_readable_possible_moves(self) -> list[str]:
        """Returns a list of human-readable possible moves."""
        all_moves_printed = []
        for move in self.valid_moves:
            all_moves_printed.append(f"{8-move[0]}{chr(move[1] + 65)} -> {8-move[2]}{chr(move[3] + 65)}")
        return all_moves_printed

    def calculate_current_valid_moves(self):
        """Generates a list of valid moves based on the current state of the board."""
        valid_moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                if self.board[row][col] == self.current_player:
                    # Check for valid moves in all possible directions
                    if 0 <= row + self.current_player_direction < len(self.board):
                        # Check right move
                        if (col + 1 < len(self.board[row])):
                            if self.board[row + self.current_player_direction][col + 1] == ' ':
                                valid_moves.append((row, col, row + self.current_player_direction, col + 1))
                            elif self.board[row + self.current_player_direction][col + 1] != self.current_player:
                                # Check for capture
                                if (row + 2 * self.current_player_direction < len(self.board) and 
                                        col + 2 < len(self.board[row]) and
                                        self.board[row + 2 * self.current_player_direction][col + 2] == ' '):
                                    valid_moves.append((row, col, row + 2 * self.current_player_direction, col + 2))
                        # Check left move
                        if (col - 1 >= 0):
                            if self.board[row + self.current_player_direction][col - 1] == ' ':
                                valid_moves.append((row, col, row + self.current_player_direction, col - 1))
                            elif self.board[row + self.current_player_direction][col - 1] != self.current_player:
                                # Check for capture
                                if (row + 2 * self.current_player_direction < len(self.board) and 
                                        col - 2 >= 0 and
                                        self.board[row + 2 * self.current_player_direction][col - 2] == ' '):
                                    valid_moves.append((row, col, row + 2 * self.current_player_direction, col - 2))

        self.valid_moves = valid_moves

    def execute_move(self, start_row: int, start_col: int, end_row: int, end_col: int):
        """Executes a move and updates the board."""
        if (end_row, end_col) in [(move[2], move[3]) for move in self.valid_moves]:
            # Move the piece
            self.board[end_row][end_col] = self.current_player
            self.board[start_row][start_col] = ' '  # Clear the starting position

            # Check for capturing an opponent piece
            if abs(start_row - end_row) == 2:  # A capture move
                captured_row = (start_row + end_row) // 2
                captured_col = (start_col + end_col) // 2
                self.board[captured_row][captured_col] = ' '  # Remove the captured piece

            # Switch the current player
            self.current_player = self.PLAYER_1_COLOR if self.current_player == self.PLAYER_2_COLOR else self.PLAYER_2_COLOR
            self.current_player_direction = self.PLAYER_BOARD_DIRECTION[self.current_player]
            self.calculate_current_valid_moves()  # Update valid moves for the next player
        else:
            print("Invalid move.")

    def mark_available(self):
        """Marks the available moves on the board."""
        if self.valid_moves:
            for move in self.valid_moves:
                self.board[move[2]][move[3]] = "G"  # Indicate valid move positions with "G"

