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

        b_size = len(self.board)
        self.board_indices = [(r, c) for c in range(b_size) for r in range(b_size)]
        self.calculate_current_valid_moves()

        self.selected_piece: tuple[int, int] | None = None

    @staticmethod
    def _check_out_of_border(col, row):
        """check if board position is actually a valid board position"""
        if 0 <= row <= 7:
            if 0 <= col <= 7:
                return False
        return True

    def human_readable_possible_moves(self) -> list[str]:
        """Returns a list of human-readable possible moves."""
        all_moves_printed = []
        for move in self.valid_moves:
            all_moves_printed.append(f"{8-move[0]}{chr(move[1] + 65)} -> {8-move[2]}{chr(move[3] + 65)}")
        return all_moves_printed

    @staticmethod
    def human_readable_possible_move(s_row, s_col, e_row, e_col):
        return f"{8-s_row}{chr(s_col + 65)} -> {8-e_row}{chr(e_col + 65)}"

    def possible_moves_for_piece(self, row, col):
        """
        ALL THE MOVES THAT ARE DONE HERE ARE WITH RESPECT TO THE MONITOR, NOT LOOKING FROM THE PLAYER PERSPECTIVE!

        in other words: "MOVE LEFT" -> "MOVE THAT DECREASE THE ALPHABET CHARACTER" (for example from "xB" -> "xA")
        "MOVE RIGHT" -> " ==.== ... INCREASE THE ALPHABET CHARACTER" (for example from "xB" -> "xC")
        """
        # initial moves -> check out of border first
        # if any "out_of_border" is true -> mark as "False" meaning move is 'invalid'
        moves_dict = {
            "move left": [
                (row + self.current_player_direction, col-1),
                not self._check_out_of_border(col-1, row + self.current_player_direction)],
            "move right": [
                (row + self.current_player_direction, col+1),
                not self._check_out_of_border(col+1, row + self.current_player_direction)],
            "beating left": [
                (row + self.current_player_direction*2, col-2),
                not self._check_out_of_border(col-2, row + self.current_player_direction * 2)],
            "beating right": [
                (row + self.current_player_direction*2, col+2),
                not self._check_out_of_border(col+2, row + self.current_player_direction * 2)],
            "beating backwards left": [
                (row - self.current_player_direction * 2, col - 2),
                not self._check_out_of_border(col - 2, row - self.current_player_direction * 2)],
            "beating backwards right": [
                (row - self.current_player_direction * 2, col + 2),
                not self._check_out_of_border(col + 2, row - self.current_player_direction * 2)],
        }
        if all([not moves_dict[k][1] for k in moves_dict]):  # all out (_not "False"_ as in -> "invalid")?
            return moves_dict  # return all false and don't check farther

        for k in moves_dict:
            # if at board, is it empty?
            if moves_dict[k][1]:
                row_, col_ = moves_dict[k][0]
                moves_dict[k][1] = self.board[row_][col_] == " "  # unobstructed -> valid move

        for k in moves_dict:
            if "beating" in k:
                row_, col_ = moves_dict[k][0]
                captured_row = (row + row_) // 2
                captured_col = (col + col_) // 2
                # is there a piece to be captured?
                if moves_dict[k][1] and (self.board[captured_row][captured_col] == self.current_enemy_player):
                    print(f"beating: {self.human_readable_possible_move(row, col, row_, col_)}")
                    moves_dict[k][1] = True
                else:
                    moves_dict[k][1] = False
        return moves_dict

    def check_lose_game(self):
        """no valid moves for player means he/she loses"""
        return self.valid_moves == []

    def calculate_current_valid_moves(self):
        """Generates a list of valid moves based on the current state of the board."""
        valid_moves = []
        for row, col in self.board_indices:
            if self.board[row][col] == self.current_player:
                # Check for valid moves in all possible directions
                moves_parsed = self.possible_moves_for_piece(row, col)
                for key in moves_parsed:
                    if moves_parsed[key][1]:
                        row_, col_ = moves_parsed[key][0]
                        valid_moves.append((row, col, row_, col_))

        self.valid_moves = valid_moves

    def switch_player(self):
        """swap enemy and current player, and change all other necessary variables"""
        # [0, 1] = [1, 0]
        self.current_player, self.current_enemy_player = self.current_enemy_player, self.current_player
        self.current_player_direction = self.PLAYER_BOARD_DIRECTION[self.current_player]

    def execute_move(self, start_row: int, start_col: int, end_row: int, end_col: int):
        """
        Executes a move and updates the board.
        This function has to be only invoked using only valid move
        """
        # Move the piece
        self.board[end_row][end_col] = self.current_player
        self.board[start_row][start_col] = ' '  # Clear the starting position

        # Check for capturing an opponent piece
        if abs(start_row - end_row) == 2:  # A capture move
            captured_row = (start_row + end_row) // 2
            captured_col = (start_col + end_col) // 2
            self.board[captured_row][captured_col] = ' '  # Remove the captured piece

    def mark_available(self):
        """Marks the available moves on the board."""
        if self.valid_moves:
            for move in self.valid_moves:
                self.board[move[2]][move[3]] = "G"  # Indicate valid move positions with "G"

    def select_piece(self, row, col):
        """check if piece is valid for selection, and enable it to choose where to move it"""
        for move in self.valid_moves:
            p_row, p_col = move[0], move[1]
            if (p_row == row) and (p_col == col):
                self.selected_piece = row, col

    def deselect_piece(self, row, col):
        """deselect the piece, if the one was selected but player does not like choice"""
        p_row, p_col = self.selected_piece
        if (p_row == row) and (p_col == col):
            self.selected_piece = None

    def clean_hints(self):
        """clean board object from all the "g" hints and such"""
        for row, col in self.board_indices:
            if self.board[row][col] == "G":
                self.board[row][col] = " "

    def show_hints_for_selection(self):
        """mark only selections that are """
        p_row, p_col = self.selected_piece
        moves_to_highlight = []
        for valid_move in self.valid_moves:
            if (valid_move[0] == p_row) and (valid_move[1] == p_col):
                self.board[valid_move[2]][valid_move[3]] = "G"

