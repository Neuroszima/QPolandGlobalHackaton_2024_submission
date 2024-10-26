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
    DARK_BOARD_COLOR = (150, 150, 150)
    POSSIBLE_MOVE_HIGHLIGHT = (0, 255, 0)  # Green square - move is possible for current player on that board space
    TEXT_COLOR = (152, 245, 249)  # Changed to white for better visibility
    QUANTUM_TEXT_COLOR = (152, 245, 249)  # Changed to white for better visibility
    COLORS_OF_PIECES = {
        "B": (95, 95, 95),     # BLACK_PIECE_COLOR
        "R": (255, 0, 0),      # RED_PIECE_COLOR
        "G": (0, 255, 0),      # GREEN_HINT_COLOR
    }

    # below are starting and end points of render spaces for certain elements of the display
    # convention: (start_x, start_y, end_x, end_y)
    BOARD_VERTICAL_ANNOTATION_RENDER_SPACE = (0, 0, 50, 800)
    BOARD_HORIZONTAL_ANNOTATION_RENDER_SPACE = (50, 800, 800, 850)
    BOARD_RENDER_SPACE = (50, 0, 850, 800)
    QUANTUM_STATE_RENDER_SPACE = (850, 0, 1250, 800)

    def __init__(self, vis_type: Literal['pygame', 'console'] | str = None):
        self.vis_type = "pygame" if vis_type is None else vis_type
        if pygame is None:
            self.vis_type = 'console'
            self.screen = None
            self.board_pixel_size = None
            self.block_size = None
            self.font_size = None
            self.quantum_font = None
        else:
            if not ((self.BOARD_RENDER_SPACE[3] - self.BOARD_RENDER_SPACE[1])
                    == (self.BOARD_RENDER_SPACE[2] - self.BOARD_RENDER_SPACE[0])):
                raise RuntimeError("Board space is not a square")
            pygame.init()  # Initialize Pygame
            self.board_pixel_size = self.BOARD_RENDER_SPACE[3] - self.BOARD_RENDER_SPACE[1]
            # Extend window size and height
            self.screen = pygame.display.set_mode((self.calculate_screen_size()))  # to fill
            self.block_size = self.board_pixel_size // 8
            self.font_size = 24
            self.quantum_font = pygame.font.SysFont('lucidaconsole', self.font_size)

        self.selected_piece = None
        self.possible_moves = []  # To track possible moves


    def draw_quantum_states(self, state_data: STATE_DATA_TYPEHINT):
        """Draw quantum states and corresponding probabilities in three columns."""
        if self.vis_type == 'console':
            self.c_draw_quantum_states(state_data)
        elif self.vis_type == 'pygame':
            self.pyg_draw_quantum_states(state_data)

    def calculate_screen_size(self):
        """based on rendered elements, get the maximum display size that comforts all the rendered elements"""
        elements = [
            self.BOARD_VERTICAL_ANNOTATION_RENDER_SPACE,
            self.BOARD_RENDER_SPACE,
            self.QUANTUM_STATE_RENDER_SPACE,
            self.BOARD_HORIZONTAL_ANNOTATION_RENDER_SPACE
        ]
        # convention: (start_x, start_y, end_x, end_y)
        max_x = 0
        max_y = 0
        for e in elements:
            if e[2] > max_x:
                max_x = e[2]
            if e[3] > max_y:
                max_y = e[3]

        return max_x, max_y
    def clear_sidebar(self):
        """Clear the sidebar area to reset it before redrawing new content."""
        start_x, start_y, end_x, end_y = self.QUANTUM_STATE_RENDER_SPACE
        # Fill the sidebar with a background color to "clear" it
        self.screen.fill((0, 0, 0), rect=(start_x, start_y, end_x - start_x, end_y - start_y))  # Black fill for sidebar

    @staticmethod
    def c_draw_quantum_states(state_data: STATE_DATA_TYPEHINT):
        """Fallback: Draw the quantum states and probabilities in the console."""
        print(f"{'State':<7} | {'Transition':<20} | {'Probability':<10}")
        print("-" * 40)
        for state, transition, probability in state_data:
            print(f"{state:<7} | {transition:<20} | {probability:<10}")

    def pyg_draw_quantum_states(self, state_data: STATE_DATA_TYPEHINT):
        """Draw quantum states and probabilities using Pygame."""
        self.clear_sidebar()  # Clear the sidebar before drawing new quantum states
        
        x_offset_state = 5  # Horizontal position for the state column
        x_offset_board_move = 125  # Horizontal position for the board move column
        x_offset_probability = 230  # Horizontal position for the probability column

        start_x, start_y, end_x, end_y = self.QUANTUM_STATE_RENDER_SPACE

        headers_y = 20
        # Draw headers
        headers = [
            ("Q-State", x_offset_state + 5),
            ("Move", x_offset_board_move + 40),
            ("Q-Prob.", x_offset_probability + 50)
        ]
        for header, x_pos in headers:
            header_surface = self.quantum_font.render(header, True, self.TEXT_COLOR)
            self.screen.blit(header_surface, (start_x + x_pos, start_y + headers_y))

        # Draw a line after the headers
        pygame.draw.line(
            self.screen, self.TEXT_COLOR,
            start_pos=(start_x, start_y + 60),
            end_pos=(end_x, start_y + 60),
            width=2
        )

        y_columns_start = 85
        y_row_separation = self.font_size + 8
        try:
            text_size = len(state_data[0][0])
        except IndexError:  # no human-readable format has been calculated yet
            text_size = 0

        if text_size == 5:
            centering_factor_state = 10
        else:
            centering_factor_state = 5

        # Draw each quantum state and its corresponding data
        for i, (state, transition, probability) in enumerate(state_data):
            row_y = start_y + y_columns_start + y_row_separation * i
            
            # State column
            state_surface = self.quantum_font.render(state, True, self.TEXT_COLOR)
            self.screen.blit(state_surface, (start_x + x_offset_state + centering_factor_state, row_y))

            # Transition column
            transition_surface = self.quantum_font.render(transition, True, self.TEXT_COLOR)
            self.screen.blit(transition_surface, (start_x + x_offset_board_move + 10, row_y))

            # Probability column
            probability_surface = self.quantum_font.render(probability, True, self.TEXT_COLOR)
            self.screen.blit(probability_surface, (start_x + x_offset_probability +50, row_y))

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
            self.screen.blit(text_surface, (i * self.block_size + 65, self.board_pixel_size + 10))  # Adjust position

    @staticmethod
    def c_possible_moves_section(human_readable_possible_moves: MOVE_RETURNED_TYPE):
        """Display possible moves in console."""
        for move in human_readable_possible_moves:
            print(move)

    # player doesn't need to have all the available moves highlighted by drawing text representations
    # instead -> make drawing hints
    # def pyg_draw_possible_moves_section(self, human_readable_possible_moves: List[str]):
    #     """Draw possible moves on the side of the board."""
    #     font = pygame.font.Font(None, 36)  # Use default font
    #     text_y = 10  # Initial y position for text
    #     max_text_height = self.board_pixel_size  # Limit to the height of the board
    #     max_moves = (max_text_height - 10) // 30  # Calculate how many moves can fit
    #     for move in human_readable_possible_moves[:max_moves]:  # Show only as many moves as fit vertically
    #         text_surface = font.render(move, True, self.TEXT_COLOR)
    #         self.screen.blit(text_surface, (self.board_pixel_size + 10, text_y))  # Draw on the right side
    #         text_y += 30  # Space between each line
    #     pygame.display.flip()

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
