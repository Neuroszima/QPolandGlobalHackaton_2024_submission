try:
    import pygame
except ImportError:
    pygame = None

from warnings import warn
from typing import Literal, List, Dict, Tuple

MOVE_RETURNED_TYPE = tuple[int, int, int, int] | tuple[float, float, float, float]

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
            self.screen = pygame.display.set_mode((window_size + 300, window_size + 50))  # Extend window size and height
            self.block_size = self.window_size // 8
        self.selected_piece = None
        self.possible_moves = []  # To track possible moves
        self.board = self.initialize_board()  # Initialize the game board
        self.current_player = 'R'  # Red starts first
        
    def draw_quantum_states(self, state_data: Dict[str, List[str]]):
        """Draw quantum states and corresponding probabilities in three columns."""
        if self.vis_type == 'console':
            self.console_draw_quantum_states(state_data)
        elif self.vis_type == 'pygame':
            self.pygame_draw_quantum_states(state_data)
            
    def console_draw_quantum_states(self, state_data: Dict[str, List[str]]):
        """Fallback: Draw the quantum states and probabilities in the console."""
        print(f"{'State':<7} | {'Transition':<20} | {'Probability':<10}")
        print("-" * 40)
        for state, (transition, probability) in state_data.items():
            print(f"{state:<7} | {transition:<20} | {probability:<10}")
            
    def pygame_draw_quantum_states(self, state_data: Dict[str, List[str]]):
        """Draw quantum states and probabilities using Pygame."""
        y_offset = 20  # Initial vertical position
        x_offset_state = 50  # Horizontal position for the state column
        x_offset_transition = 200  # Horizontal position for the transition column
        x_offset_probability = 450  # Horizontal position for the probability column

        self.screen.fill((0, 0, 0))  # Clear the screen with black background

        # Draw headers
        headers = [("State", x_offset_state), ("Transition", x_offset_transition), ("Probability", x_offset_probability)]
        for header, x_pos in headers:
            header_surface = self.font.render(header, True, self.TEXT_COLOR)
            self.screen.blit(header_surface, (x_pos, y_offset))

        # Draw a line after the headers
        pygame.draw.line(self.screen, self.TEXT_COLOR, (x_offset_state, y_offset + 30), (x_offset_probability + 150, y_offset + 30), 2)

        # Increment y position for data
        y_offset += 50

        # Draw each quantum state and its corresponding data
        for state, (transition, probability) in state_data.items():
            # State column
            state_surface = self.font.render(state, True, self.TEXT_COLOR)
            self.screen.blit(state_surface, (x_offset_state, y_offset))

            # Transition column
            transition_surface = self.font.render(transition, True, self.TEXT_COLOR)
            self.screen.blit(transition_surface, (x_offset_transition, y_offset))

            # Probability column
            probability_surface = self.font.render(probability, True, self.TEXT_COLOR)
            self.screen.blit(probability_surface, (x_offset_probability, y_offset))

            # Move to next row
            y_offset += 40

        pygame.display.flip()

            

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

    def c_possible_moves_section(self, human_readable_possible_moves: List[str]):
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
                    if self.board[new_y][new_x] != ' ' and self.board[capture_y][capture_x] == ' ':
                        valid_moves.append((capture_y, capture_x))  # Add capture move
        return valid_moves

    def move_piece(self, from_coords: Tuple[int, int], to_coords: Tuple[int, int]):
        """Move a piece from one location to another."""
        y_from, x_from = from_coords
        y_to, x_to = to_coords
        self.board[y_to][x_to] = self.board[y_from][x_from]  # Move piece to new location
        self.board[y_from][x_from] = ' '  # Empty the original spot

    def run(self):
        """Main game loop for Pygame rendering."""
        if self.vis_type == 'console':
            while True:
                self.c_draw_board(self.board)
                # Example: handle user input or break loop
                # Implement your logic for handling user input here
        elif self.vis_type == 'pygame':
            self.pyg_display_title()  # Set the game title
            running = True
            while running:
                self.screen.fill((0, 0, 0))  # Fill the screen with black
                self.pyg_draw_board(self.board)  # Draw the board
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                        pos = pygame.mouse.get_pos()
                        self.pyg_handle_click_select_piece(pos)  # Handle piece selection
                pygame.display.flip()  # Update the display
            pygame.quit()  # Close Pygame

if __name__ == '__main__':
    engine = GameDisplayEngine(vis_type='pygame', window_size=600)
    engine.run()