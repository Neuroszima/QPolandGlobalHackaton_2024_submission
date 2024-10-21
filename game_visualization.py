try:
    import pygame
except ImportError:
    pygame = None
from typing import Literal


class GameEngine:
    """
    Everything connected to drawing pieces, game state, board etc. in console or in pygame
    Also handles on_click events/mouse_data for pygame side of the game interactions
    """
    GAME_TITLE = "Checkers Game"
    LIGHT_BOARD_COLOR = (255, 255, 255)
    DARK_BOARD_COLOR = (0, 0, 0)
    POSSIBLE_MOVE_HIGHLIGHT = (0, 255, 0)  # green square - move is possible for current player on that board space

    def __init__(self, vis_type: Literal['pygame', 'console'] = None,  window_size: int = 600):
        self.vis_type = "pygame" if vis_type is None else vis_type
        self.window_size = window_size
        if pygame is None:
            self.vis_type = 'console'
            self.screen = None
            self.window_size = None
        else:
            self.window_size = window_size
            self.screen = pygame.display.set_mode((window_size, window_size))
        self.selected_piece = None

    def pyg_get_square(self, pos):
        """retreive 2D board coordinates from mouse_click events"""
        # below needs to account for the board space only, not the space reserved for additional information
        # for example exclude the section with checkers bot engine possible moves visualizer
        # I am inclined to show this information on the right side, since this is what top Chess engines do when
        # visualizing their possible moves and top % chances, like for example stockfish in the video here:
        #
        block_size = self.window_size // 8  # - self.possible_move_window_section_X
        x, y = pos
        return x // block_size, y // block_size

    def c_draw_board(self, board: list[list]):
        """draw board for console type of rendering"""
        for index, row in enumerate(board):
            print("  -" + "----"*8)
            r_print = f"{len(board)-index} |"
            for board_spot in row:
                r_print += f" {board_spot} |"
            print(r_print)
        print("  -" + "----"*8)
        print("   " + "".join([f" {chr(col+65)}  " for col in range(8)]))

    def pyg_draw_board(self, board: list[list]):
        """draw the base board version in window for pygame type of rendering"""
        block_size = self.window_size // 8  # Checkers board is 8x8
        for y in range(8):
            for x in range(8):
                rect = pygame.Rect(x * block_size, y * block_size, block_size, block_size)
                color = self.LIGHT_BOARD_COLOR if (x + y) % 2 == 0 else self.DARK_BOARD_COLOR
                pygame.draw.rect(self.screen, color, rect)

                # Draw the checkers
                piece = board[y][x]
                if piece == 'R':  # Red piece
                    pygame.draw.circle(self.screen, (255, 0, 0), (
                        x * block_size + block_size // 2, y * block_size + block_size // 2), block_size // 2 - 5)
                elif piece == 'B':  # Black piece
                    pygame.draw.circle(self.screen, (0, 0, 0), (
                        x * block_size + block_size // 2, y * block_size + block_size // 2), block_size // 2 - 5)

        pygame.display.flip()

    def c_possible_moves_section(self, human_readable_possible_moves: list[str]):
        for move in human_readable_possible_moves:
            print(move)

    def pyg_draw_possible_moves_section(self, human_readable_possible_moves: list[str]):
        """
        draw a top 10 or 10 preselected moves from list of moves that are possible for the player
        draw them on the side, in a narrow column, one below another
        """
        # to be determined how to draw, i encourage light-blue font (this will alwyas be about 8-7 characters long)
        # on black background on the side of the board.

        # This will in future become visualizer of the move probabilities (for the bot player), so leave spot
        # for "XX.XX%" text for future use
        # you can mock this "XX.XX%" for now, to see how the text is laid out, to make it visible for future
        # for the human-controlled player, the space will be just empty

        # on top of the narrow section on the side of the board include text "possible player moves", can be one word
        # below another to save space
        pass

    def pyg_overlay_possible_selected_moves(self):
        """
        draw possible moves for selected piece, by overlaying "Highlight square" over the space that corresponds to
        these possible moves
        """
        pass

    def pyg_handle_click_select_piece(
            self, pos, player_color: str, player_direction: int, board: list[list], possible_moves: list[tuple[int]]):
        """
        select piece with mouseclick
        we could move piece with separate method, after selecting correct one and highlighting possible moves,
        that this particular selected piece can make (for example with redish-orange color, in separate method as well)
        """

        # global selected_piece, possible_moves
        x, y = self.pyg_get_square(pos)
        if self.selected_piece is None:  # Select a piece
            if board[y][x] == player_color:  # Only allow currently controlling players pieces to be selected
                selected_piece = (y, x)
                # possible_moves = checkers_bot_logic.get_valid_moves(board, player_color, player_direction)  # Get valid moves
        else:  # Move the selected piece
            # start_row, start_col = self.selected_piece
            # if (y, x) in [(move[2], move[3]) for move in possible_moves if move[0] == start_row and move[1] == start_col]:
            #     move_piece(start_row, start_col, y, x)
            selected_piece = None
            possible_moves = []
        self.selected_piece = selected_piece

    def pyg_display_title(self):
        pygame.display.set_caption("Checkers Game")


