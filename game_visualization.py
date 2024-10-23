try:
    import pygame
except ImportError:
    pygame = None

from warnings import warn
from typing import Literal, List, Tuple
MOVE_RETURNED_TYPE = tuple[int, int, int, int] | tuple[float, float, float, float]


class GameDisplayEngine:
    """
    Everything connected to drawing pieces, game state, board etc. in console or in pygame
    Also handles on_click events/mouse_data for pygame side of the game interactions

    ONLY DRAWING + WINDOW INTERACTION, NO LOGIC LIKE CALCULATING LEGAL MOVES!!!
    """
    GAME_TITLE = "Checkers Game"
    LIGHT_BOARD_COLOR = (255, 255, 255)
    DARK_BOARD_COLOR = (169, 169, 169)
    POSSIBLE_MOVE_HIGHLIGHT = (0, 255, 0)  # Green square - move is possible for current player on that board space
    TEXT_COLOR = (173, 216, 230)  # Light blue color for possible moves text
    COLORS_OF_PIECES = {
        "B": (105, 105, 105),  # BLACK_PIECE_COLOR
        "R": (255, 0, 0),      # RED_PIECE_COLOR
        "G": (0, 255, 0),      # GREEN_HINT_COLOR
    }

    def __init__(self, vis_type: Literal['pygame', 'console'] = None, window_size: int = 600):
        self.vis_type = "pygame" if vis_type is None else vis_type
        self.window_size = window_size
        if pygame is None:
            self.vis_type = 'console'
            self.screen = None
            self.window_size = None
            self.block_size = None
        else:
            pygame.init()  # Initialize Pygame
            self.window_size = window_size
            self.screen = pygame.display.set_mode((window_size, window_size))
            self.block_size = self.window_size // 8
        self.selected_piece = None
        self.possible_moves = []  # To track possible moves
        self.board = self.initialize_board()  # Initialize the game board
        self.current_player = 'R'  # Red starts first

    def initialize_board(self) -> List[List[str]]:
        """Initialize the checkers board with pieces."""
        board = [[' ' for _ in range(8)] for _ in range(8)]
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = 'B'  # Black pieces
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = 'R'  # Red pieces
        return board

    def pyg_get_square(self, pos) -> Tuple[int, int]:
        """Retrieve 2D board coordinates from mouse click events."""
        # block_size = self.window_size // 8
        x, y = pos
        return x // self.block_size, y // self.block_size

    def c_draw_board(self, board: List[List[str]]):
        """Draw board for console type of rendering."""
        for index, row in enumerate(board):
            print("  -" + "----" * 8)
            r_print = f"{len(board) - index} |"
            for board_spot in row:
                r_print += f" {board_spot} |"
            print(r_print)
        print("  -" + "----" * 8)
        print("   " + "".join([f" {chr(col + 65)}  " for col in range(8)]))

    def pyg_draw_board(self, board: List[List[str]]):
        """Draw the base board version in window for pygame type of rendering."""
        for y in range(8):
            for x in range(8):
                rect = pygame.Rect(x * self.block_size, y * self.block_size, self.block_size, self.block_size)
                color = self.LIGHT_BOARD_COLOR if (x + y) % 2 == 0 else self.DARK_BOARD_COLOR
                pygame.draw.rect(self.screen, color, rect)

                # Draw the checkers
                piece = board[y][x]
                if piece == " ":
                    continue
                pygame.draw.circle(
                    surface=self.screen,
                    color=self.COLORS_OF_PIECES[piece],
                    center=((x + 0.5) * self.block_size, (y + 0.5) * self.block_size),
                    radius=self.block_size // 2 - 5
                )

        # pygame.display.flip()

    def c_possible_moves_section(self, human_readable_possible_moves: List[str]):
        """Display possible moves in console."""
        for move in human_readable_possible_moves:
            print(move)

    def pyg_draw_possible_moves_section(self, human_readable_possible_moves: List[str]):
        """Draw possible moves on the side of the board."""
        font = pygame.font.Font(None, 36)  # Use default font
        text_y = 10  # Initial y position for text
        for move in human_readable_possible_moves[:10]:  # Show top 10 moves
            text_surface = font.render(move, True, self.TEXT_COLOR)
            self.screen.blit(text_surface, (self.window_size - 150, text_y))  # Draw on the right side
            text_y += 30  # Space between each line
        pygame.display.flip()

    def pyg_overlay_possible_selected_moves(self):
        """Highlight possible moves for the selected piece."""
        if self.selected_piece is not None:
            block_size = self.window_size // 8
            for move in self.possible_moves:
                x, y = move
                rect = pygame.Rect(x * block_size, y * block_size, block_size, block_size)
                pygame.draw.rect(self.screen, self.POSSIBLE_MOVE_HIGHLIGHT, rect, 5)  # Draw a border for possible moves
            pygame.display.flip()


    def pyg_handle_click_select_piece(self, pos):
        """
        Select piece with mouse click and highlight possible moves.
        """
        warn("this function will be replaced or changed", category=DeprecationWarning, stacklevel=2)
        x, y = self.pyg_get_square(pos)
        if self.selected_piece is None:  # Select a piece
            if self.board[y][x] == self.current_player:  # Only allow currently controlling player's pieces to be selected
                self.selected_piece = (y, x)
                self.possible_moves = self.get_valid_moves(self.selected_piece)  # Get valid moves for selected piece
                self.pyg_overlay_possible_selected_moves()  # Highlight moves
        else:  # Move the selected piece
            if (y, x) in self.possible_moves:
                self.move_piece(self.selected_piece, (y, x))  # Move piece on the board
                self.selected_piece = None  # Deselect after move
                self.possible_moves = []  # Clear possible moves
                self.current_player = 'B' if self.current_player == 'R' else 'R'  # Switch players
            else:
                print("Invalid move!")  # Error feedback

    def pyg_handle_click(self, pos, valid_moves) -> MOVE_RETURNED_TYPE | None:
        """
        check if clicked spot corresponds to some action, and return identifier if it happens so accordingly

        for now it only returns valid move combination of starting and ending coordinates
        """
        x, y = self.pyg_get_square(pos)
        if valid_moves:
            # idea for testing: sort by key=lambda v_move: v_move[0]?
            # meaning: sort by start row to get the priority on "left oriented" moves first?
            for move in valid_moves:
                if (y, x) == (move[2], move[3]):
                    return move

    def pyg_display_title(self):
        """Set the game window title."""
        pygame.display.set_caption(self.GAME_TITLE)

    def get_valid_moves(self, selected_piece: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Determine valid moves for the selected piece."""
        location = f"{self.__class__}.{self.get_valid_moves.__name__}"
        warn(f"this function, due to the fact that it contains logic for game ruleset, "
             f"shouldn't be here\n{location}", category=DeprecationWarning, stacklevel=2)
        y, x = selected_piece
        directions = [1, -1]  # Directions for moving down or up the board
        valid_moves = []
        for direction in directions:
            for dx in [-1, 1]:  # Left and right
                new_y = y + direction
                new_x = x + dx
                if 0 <= new_y < 8 and 0 <= new_x < 8 and self.board[new_y][new_x] == ' ':
                    valid_moves.append((new_y, new_x))  # Add valid move
                # Capture move
                capture_y = y + 2 * direction
                capture_x = x + 2 * dx
                if 0 <= new_y < 8 and 0 <= new_x < 8 and 0 <= capture_y < 8 and 0 <= capture_x < 8:
                    if self.board[new_y][new_x] != ' ' and self.board[new_y][new_x] != self.current_player:
                        if self.board[capture_y][capture_x] == ' ':
                            valid_moves.append((capture_y, capture_x))  # Add capture move
        return valid_moves

    def move_piece(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]):
        """Move a piece on the board and handle capture logic."""
        location = f"{self.__class__}.{self.get_valid_moves.__name__}"
        warn(f"this function, due to the fact that it contains logic for game ruleset, "
             f"shouldn't be here\n{location}", category=DeprecationWarning, stacklevel=2)

        # you may change this to include new position
        y_from, x_from = from_pos
        y_to, x_to = to_pos
        self.board[y_to][x_to] = self.board[y_from][x_from]  # Move piece
        self.board[y_from][x_from] = ' '  # Empty the original spot

        # Check for capturing
        if abs(y_from - y_to) == 2:
            mid_y = (y_from + y_to) // 2
            mid_x = (x_from + x_to) // 2
            self.board[mid_y][mid_x] = ' '  # Remove captured piece

