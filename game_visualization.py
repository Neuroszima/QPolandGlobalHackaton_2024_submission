try:
    import pygame
except ImportError:
    pygame = None

from typing import Literal, List, Tuple

CLICK_RETURNED_TYPE = tuple[tuple[int, int], str] | tuple[list[int, int], str]
BOARD_TYPEHINT = list[list[str]]
STATE_DATA_TYPEHINT = list[str, str, str]
MOVES_LIST_TYPEHINT = list[list[int, int, int, int]] | list[tuple[int, int, int, int]]


class GameDisplayEngine:
    """
    Everything connected to drawing pieces, game state, board, etc., in console or in pygame.
    Also handles on_click events/mouse_data for pygame side of the game interactions.
    ONLY DRAWING + WINDOW INTERACTION, NO LOGIC LIKE CALCULATING LEGAL MOVES!!!
    """
    GAME_TITLE = "Checkers Game"
    LIGHT_BOARD_COLOR = (255, 255, 255)
    DARK_BOARD_COLOR = (140, 140, 140)
    POSSIBLE_MOVE_HIGHLIGHT = (0, 255, 0)  # for now it is green but can be any
    QUANTUM_TEXT_COLOR = (152, 245, 249)  # Changed to white for better visibility
    BOARD_MARKER_TEXT_COLOR = (204, 255, 255)  # very light blue/violet
    LAST_MOVE_HIGHLIGHT_COLOR = (255, 166, 77)  # for now this will be yellow/orange
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
            self.screen = pygame.display.set_mode((self.pyg_calculate_screen_size()))  # to fill
            self.block_size = self.board_pixel_size // 8
            self.font_size = 24
            try:
                self.quantum_font = pygame.font.SysFont('lucidaconsole', self.font_size)
            except Exception:  # font not found
                self.quantum_font = pygame.font.SysFont('arial', self.font_size)
            try:
                self.board_marker_font = pygame.font.SysFont('tahoma', int(self.font_size * 1.5))
            except Exception:  # font not found
                self.board_marker_font = pygame.font.SysFont('arial', int(self.font_size * 1.5))

        self.regions = [
            self.QUANTUM_STATE_RENDER_SPACE,
            self.BOARD_RENDER_SPACE,
            self.BOARD_VERTICAL_ANNOTATION_RENDER_SPACE,
            self.BOARD_HORIZONTAL_ANNOTATION_RENDER_SPACE
        ]
        self.selected_piece = None
        self.possible_moves = []  # To track possible moves


        # horizontal_middlepoint = (
        #         self.BOARD_VERTICAL_ANNOTATION_RENDER_SPACE[2] -
        #         self.BOARD_VERTICAL_ANNOTATION_RENDER_SPACE[0]) - (self.font_size * 3/4)
        #
        # vertical_middlepoint = (
        #         self.BOARD_HORIZONTAL_ANNOTATION_RENDER_SPACE[3] -
        #         self.BOARD_HORIZONTAL_ANNOTATION_RENDER_SPACE[1]) - (self.font_size * 3/4)
        # print(f"{horizontal_middlepoint=}", f"{vertical_middlepoint=}")

    @staticmethod
    def c_possible_moves_section(human_readable_possible_moves: list):
        """Display possible moves in console."""
        for move in human_readable_possible_moves:
            print(move)

    @staticmethod
    def c_draw_quantum_states(state_data: STATE_DATA_TYPEHINT):
        """Fallback: Draw the quantum states and probabilities in the console."""
        print(f"{'State':<7} | {'Transition':<20} | {'Probability':<10}")
        print("-" * 40)
        for state, transition, probability in state_data:
            print(f"{state:<7} | {transition:<20} | {probability:<10}")

    @staticmethod
    def c_draw_board(board: List[List[str]]):
        """Draw board for console type of rendering."""
        for index, row in enumerate(board):
            print("  -" + "----" * 8)
            r_print = f"{len(board) - index} |"
            for board_spot in row:
                r_print += f" {board_spot} |"
            print(r_print)
        print("  -" + "----" * 8)
        print("   " + "".join([f" {chr(col + 65)}  " for col in range(8)]))
        
    def pyg_draw_win_lose_message(self, message: str):
        """Display a centered win/lose message."""
        # the font and color
        font = pygame.font.SysFont('arial', 48)
        color = (255, 255, 255) 

        # Render the message
        text_surface = font.render(message, True, color)
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))

        # Draw a semi-transparent background rectangle behind the message
        background_rect = text_rect.inflate(20, 20)  # padding around the message
        pygame.draw.rect(self.screen, (0, 0, 0, 128), background_rect)  # Black with some transparency

        # Display the message on the screen
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()  # Update the display
        
    @staticmethod
    def pyg_click_within_region(start_x, start_y, end_x, end_y, click_x, click_y):
        """detect if event happened to be in the region"""
        if start_x < click_x < end_x:
            if start_y < click_y < end_y:
                return True
        return False

    def draw_quantum_states(self, state_data: STATE_DATA_TYPEHINT):
        """Draw quantum states and corresponding probabilities in three columns."""
        if self.vis_type == 'console':
            self.c_draw_quantum_states(state_data)
        elif self.vis_type == 'pygame':
            self.pyg_draw_quantum_states(state_data)

    def pyg_calculate_screen_size(self):
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

    def pyg_clear_sidebar(self):
        """Clear the sidebar area to reset it before redrawing new content."""
        start_x, start_y, end_x, end_y = self.QUANTUM_STATE_RENDER_SPACE
        # Fill the sidebar with a background color to "clear" it
        self.screen.fill((0, 0, 0), rect=(
            start_x, start_y, end_x - start_x, end_y - start_y))  # Black fill for sidebar

    def pyg_draw_quantum_states(self, state_data: STATE_DATA_TYPEHINT):
        """Draw quantum states and probabilities using Pygame."""
        self.pyg_clear_sidebar()  # Clear the sidebar before drawing new quantum states
        
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
            header_surface = self.quantum_font.render(header, True, self.QUANTUM_TEXT_COLOR)
            self.screen.blit(header_surface, (start_x + x_pos, start_y + headers_y))

        # Draw a line after the headers
        pygame.draw.line(
            self.screen, self.QUANTUM_TEXT_COLOR,
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

            if i == 0:
                t_color = self.LAST_MOVE_HIGHLIGHT_COLOR
            else:
                t_color = self.QUANTUM_TEXT_COLOR
            
            # State column
            state_surface = self.quantum_font.render(state, True, t_color)
            self.screen.blit(state_surface, (start_x + x_offset_state + centering_factor_state, row_y))

            # Transition column
            transition_surface = self.quantum_font.render(transition, True, t_color)
            self.screen.blit(transition_surface, (start_x + x_offset_board_move + 10, row_y))

            # Probability column
            probability_surface = self.quantum_font.render(probability, True, t_color)
            self.screen.blit(probability_surface, (start_x + x_offset_probability + 50, row_y))

        pygame.display.flip()

    def pyg_get_board_square(self, click_pos) -> Tuple[int, int]:
        """Retrieve 2D board coordinates from mouse click events."""
        x, y = click_pos
        # Adjust the coordinates to account for clicking on board render space, instead of hardcoding
        board_column = (x - self.BOARD_RENDER_SPACE[0]) // self.block_size
        board_row = (y - self.BOARD_RENDER_SPACE[1]) // self.block_size
        return board_row, board_column

    def pyg_draw_bottom_board_markers(self):
        """Draw column letters (A to H) at the bottom"""
        # 3/4 -> this is because this font is "1.5x bigger" but "we take middle, so 1/2"
        vertical_middlepoint = (
                self.BOARD_HORIZONTAL_ANNOTATION_RENDER_SPACE[3] -
                self.BOARD_HORIZONTAL_ANNOTATION_RENDER_SPACE[1]) - (self.font_size * 3/4)
        for i in range(8):
            text_surface = self.board_marker_font.render(
                chr(i + 65), True, self.BOARD_MARKER_TEXT_COLOR)  # 65 is ASCII for 'A'

            # with adjust position
            self.screen.blit(text_surface, (
                self.BOARD_HORIZONTAL_ANNOTATION_RENDER_SPACE[0] + self.block_size * (i + 0.5) - self.font_size/2,
                self.BOARD_HORIZONTAL_ANNOTATION_RENDER_SPACE[1],  # - vertical_middlepoint
            ))

    def pyg_draw_side_board_markers(self):
        """Draw column letters (A to H) at the bottom"""
        # 3/4 -> this is because this font is "1.5x bigger" but "we take middle, so 1/2"
        horizontal_middlepoint = (
                self.BOARD_VERTICAL_ANNOTATION_RENDER_SPACE[2] -
                self.BOARD_VERTICAL_ANNOTATION_RENDER_SPACE[0])/2 - (self.font_size * 1/4)
        for i in range(8):
            text_surface = self.board_marker_font.render(
                str(8 - i), True, self.BOARD_MARKER_TEXT_COLOR)  # 65 is ASCII for 'A'

            # with adjust position
            self.screen.blit(text_surface, (
                self.BOARD_VERTICAL_ANNOTATION_RENDER_SPACE[0] + horizontal_middlepoint,
                self.BOARD_VERTICAL_ANNOTATION_RENDER_SPACE[1] + self.block_size * (i + 0.5) - self.font_size,
            ))

    def pyg_draw_board(self, board: List[List[str]], selected_piece, hints_for_selection, previous_move_coordinates):
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

        # separated into their own methods
        self.pyg_draw_move_hints(selected_piece, hints_for_selection)
        self.pyg_draw_side_board_markers()
        self.pyg_draw_bottom_board_markers()
        self.pyg_draw_last_player_move(previous_move_coordinates)

    def pyg_overlay_possible_selected_moves(self):
        """Highlight possible moves for the selected piece."""
        if self.selected_piece is not None:
            for move in self.possible_moves:
                x, y = move
                # Adjust for x
                rect = pygame.Rect(x * self.block_size + 50, y * self.block_size, self.block_size, self.block_size)
                pygame.draw.rect(self.screen, self.POSSIBLE_MOVE_HIGHLIGHT, rect, 5)  # Draw a border for possible moves
            pygame.display.flip()

    def pyg_handle_click(self, pos: tuple[int, int]) -> CLICK_RETURNED_TYPE | None:
        """
        Check if clicked spot corresponds to some action, and return identifier if it happens so accordingly.

        For now, it only returns valid move combination of starting and ending coordinates.
        """
        if self.pyg_click_within_region(*self.BOARD_RENDER_SPACE, *pos):
            board_row, board_col = self.pyg_get_board_square(pos)
            return (board_row, board_col), "board"
        return (-1, -1), "none"

    def pyg_display_title(self):
        """Set the game window title."""
        pygame.display.set_caption(self.GAME_TITLE)

    def pyg_draw_move_hints(self, selected_board_space: tuple[int, int] | None, hint_coordinates: list[tuple] | None):
        """
        draw green circles that correspond to available moves, that can be done with respect
        to selected piece

        :param selected_board_space: row and column of actual board instance, where the starting piece is located
        :param hint_coordinates: list of possible coordinates for moves starting piece can take
        """
        transparent_hint_surface = pygame.Surface((self.block_size, self.block_size), pygame.SRCALPHA)
        transparent_hint_surface.fill((0, 200, 0, 40))

        if selected_board_space:
            row, column = selected_board_space
            self.screen.blit(transparent_hint_surface, dest=(
                    self.BOARD_RENDER_SPACE[0] + self.block_size * column,
                    self.BOARD_RENDER_SPACE[1] + self.block_size * row
                ))

        if hint_coordinates:
            for board_row, board_column in hint_coordinates:
                self.screen.blit(transparent_hint_surface, dest=(
                    self.BOARD_RENDER_SPACE[0] + self.block_size * board_column,
                    self.BOARD_RENDER_SPACE[1] + self.block_size * board_row
                ))

    def pyg_draw_last_player_move(self, last_moves: list[tuple] | None):
        """
        draw colored, transparent squares that correspond to action execution of last player
        logic is the same as in `pyg_draw_move_hints`

        :param last_moves: list of tuples with coordinates
        """
        transparent_hint_surface = pygame.Surface((self.block_size, self.block_size), pygame.SRCALPHA)
        transparent_hint_surface.fill((*self.LAST_MOVE_HIGHLIGHT_COLOR, 40))

        if last_moves:
            for board_row, board_column in last_moves:
                self.screen.blit(transparent_hint_surface, dest=(
                    self.BOARD_RENDER_SPACE[0] + self.block_size * board_column,
                    self.BOARD_RENDER_SPACE[1] + self.block_size * board_row
                ))
