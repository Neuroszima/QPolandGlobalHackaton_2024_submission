try:
    import pygame
except ImportError:
    pygame = None

from warnings import warn
from typing import Literal, List, Tuple

MOVE_RETURNED_TYPE = tuple[int, int, int, int] | tuple[float, float, float, float]
BOARD_TYPEHINT = list[list[str]]
STATE_DATA_TYPEHINT = list[str, str, str]


class GameDisplayEngine:
    """
    Everything connected to drawing pieces, game state, board, etc., in console or in pygame.
    Also handles on_click events/mouse_data for pygame side of the game interactions.
    ONLY DRAWING + WINDOW INTERACTION, NO LOGIC LIKE CALCULATING LEGAL MOVES!!!
    """
    GAME_TITLE = "Checkers Game"
    LIGHT_BOARD_COLOR = (255, 255, 255)
    DARK_BOARD_COLOR = (169, 169, 169)
    POSSIBLE_MOVE_HIGHLIGHT = (0, 255, 0)  # Green square - move is possible for current player on that board space
    TEXT_COLOR = (255, 255, 255)  # Changed to white for better visibility
    COLORS_OF_PIECES = {
        "B": (105, 105, 105),  # BLACK_PIECE_COLOR
        "R": (255, 0, 0),      # RED_PIECE_COLOR
        "G": (0, 255, 0),      # GREEN_HINT_COLOR
    }

    START_CORNER_BOARD = ()

    def __init__(self, vis_type: Literal['pygame', 'console'] | str = None, window_size: int = 600):
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
            self.screen = pygame.display.set_mode((window_size + 300, window_size + 50))  # Extend window size and height
            self.block_size = self.window_size // 8
        self.selected_piece = None
        self.possible_moves = []  # To track possible moves

        self.quantum_font = pygame.font.SysFont('sans mono', 24)

    def draw_quantum_states(self, state_data: STATE_DATA_TYPEHINT):
        """Draw quantum states and corresponding probabilities in three columns."""
        if self.vis_type == 'console':
            self.c_draw_quantum_states(state_data)
        elif self.vis_type == 'pygame':
            self.pyg_draw_quantum_states(state_data)

    @staticmethod
    def c_draw_quantum_states(state_data: STATE_DATA_TYPEHINT):
        """Fallback: Draw the quantum states and probabilities in the console."""
        print(f"{'State':<7} | {'Transition':<20} | {'Probability':<10}")
        print("-" * 40)
        for state, transition, probability in state_data:
            print(f"{state:<7} | {transition:<20} | {probability:<10}")

    def pyg_draw_quantum_states(self, state_data: STATE_DATA_TYPEHINT):
        """Draw quantum states and probabilities using Pygame."""
        y_offset = 20  # Initial vertical position
        x_offset_state = 50  # Horizontal position for the state column
        x_offset_transition = 200  # Horizontal position for the transition column
        x_offset_probability = 450  # Horizontal position for the probability column

        self.screen.fill((0, 0, 0))  # Clear the screen with black background

        # Draw headers
        headers = [("State", x_offset_state), ("Transition", x_offset_transition), ("Probability", x_offset_probability)]
        for header, x_pos in headers:
            header_surface = self.quantum_font.render(header, True, self.TEXT_COLOR)
            self.screen.blit(header_surface, (x_pos, y_offset))

        # Draw a line after the headers
        pygame.draw.line(
            self.screen, self.TEXT_COLOR,
            start_pos=(x_offset_state, y_offset + 30),
            end_pos=(x_offset_probability + 150, y_offset + 30),
            width=2
        )

        # Increment y position for data
        y_offset += 50

        # Draw each quantum state and its corresponding data
        for state, transition, probability in state_data:
            # State column
            state_surface = self.quantum_font.render(state, True, self.TEXT_COLOR)
            self.screen.blit(state_surface, (x_offset_state, y_offset))

            # Transition column
            transition_surface = self.quantum_font.render(transition, True, self.TEXT_COLOR)
            self.screen.blit(transition_surface, (x_offset_transition, y_offset))

            # Probability column
            probability_surface = self.quantum_font.render(probability, True, self.TEXT_COLOR)
            self.screen.blit(probability_surface, (x_offset_probability, y_offset))

            # Move to next row
            y_offset += 40

        pygame.display.flip()

    def pyg_get_square(self, pos) -> Tuple[int, int]:
        """Retrieve 2D board coordinates from mouse click events."""
        x, y = pos
        # Adjust the coordinates to account for padding
        adjusted_x = (x - 50) // self.block_size  # 50 pixels of padding on the left
        adjusted_y = y // self.block_size  # No padding at the top
        return adjusted_x, adjusted_y

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
                rect = pygame.Rect(x * self.block_size + 50, y * self.block_size, self.block_size, self.block_size)
                color = self.LIGHT_BOARD_COLOR if (x + y) % 2 == 0 else self.DARK_BOARD_COLOR
                pygame.draw.rect(self.screen, color, rect)

                # Draw the checkers
                piece = board[y][x]
                if piece == " ":
                    continue
                pygame.draw.circle(
                    surface=self.screen,
                    color=self.COLORS_OF_PIECES[piece],
                    center=((x + 0.5) * self.block_size + 50, (y + 0.5) * self.block_size),
                    radius=self.block_size // 2 - 5
                )

        # Draw row numbers (1 to 8) on the left side
        font = pygame.font.Font(None, 36)  # Use default font
        for i in range(8):
            text_surface = font.render(str(8 - i), True, self.TEXT_COLOR)
            self.screen.blit(text_surface, (15, i * self.block_size + 15))  # Adjust position as needed

        # Draw column letters (A to H) at the bottom
        for i in range(8):
            text_surface = font.render(chr(i + 65), True, self.TEXT_COLOR)  # 65 is ASCII for 'A'
            self.screen.blit(text_surface, (i * self.block_size + 65, self.window_size + 10))  # Adjust position

    @staticmethod
    def c_possible_moves_section(human_readable_possible_moves: MOVE_RETURNED_TYPE):
        """Display possible moves in console."""
        for move in human_readable_possible_moves:
            print(move)

    def pyg_draw_possible_moves_section(self, human_readable_possible_moves: List[str]):
        """Draw possible moves on the side of the board."""
        font = pygame.font.Font(None, 36)  # Use default font
        text_y = 10  # Initial y position for text
        max_text_height = self.window_size  # Limit to the height of the board
        max_moves = (max_text_height - 10) // 30  # Calculate how many moves can fit
        for move in human_readable_possible_moves[:max_moves]:  # Show only as many moves as fit vertically
            text_surface = font.render(move, True, self.TEXT_COLOR)
            self.screen.blit(text_surface, (self.window_size + 10, text_y))  # Draw on the right side
            text_y += 30  # Space between each line
        pygame.display.flip()

    def pyg_overlay_possible_selected_moves(self):
        """Highlight possible moves for the selected piece."""
        if self.selected_piece is not None:
            for move in self.possible_moves:
                x, y = move
                rect = pygame.Rect(x * self.block_size + 50, y * self.block_size, self.block_size, self.block_size)  # Adjust for x
                pygame.draw.rect(self.screen, self.POSSIBLE_MOVE_HIGHLIGHT, rect, 5)  # Draw a border for possible moves
            pygame.display.flip()

    def pyg_handle_click(self, pos, valid_moves) -> MOVE_RETURNED_TYPE | None:
        """
        Check if clicked spot corresponds to some action, and return identifier if it happens so accordingly.

        For now it only returns valid move combination of starting and ending coordinates.
        """
        x, y = self.pyg_get_square(pos)
        if valid_moves:
            for move in valid_moves:
                if (y, x) == (move[2], move[3]):
                    return move

    def pyg_display_title(self):
        """Set the game window title."""
        pygame.display.set_caption(self.GAME_TITLE)
