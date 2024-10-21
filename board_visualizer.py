try:
    import pygame
except ImportError:
    pygame = None

import checkers_bot_logic


if pygame:
    # Initialize pygame
    pygame.init()

    # Create a window for displaying the board
    window_size = 600
    screen = pygame.display.set_mode((window_size, window_size))
    pygame.display.set_caption("Checkers Game")


# Define colors for the checkers board
white = (255, 255, 255)
black = (0, 0, 0)

# Game variables
board = [
    [' ', 'B', ' ', 'B', ' ', 'B', ' ', 'B'],
    ['B', ' ', 'B', ' ', 'B', ' ', 'B', ' '],
    [' ', 'B', ' ', 'B', ' ', 'B', ' ', 'B'],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ['R', ' ', 'R', ' ', 'R', ' ', 'R', ' '],
    [' ', 'R', ' ', 'R', ' ', 'R', ' ', 'R'],
    ['R', ' ', 'R', ' ', 'R', ' ', 'R', ' ']
]

starting_color = "R"
current_color = starting_color
defending_color = "B"
if current_color == "R":
    player_direction = -1
else:
    player_direction = 1
selected_piece = None
possible_moves = []


def draw_board():
    if pygame:
        block_size = window_size // 8  # Checkers board is 8x8
        for y in range(8):
            for x in range(8):
                rect = pygame.Rect(x * block_size, y * block_size, block_size, block_size)
                color = white if (x + y) % 2 == 0 else black
                pygame.draw.rect(screen, color, rect)

                # Draw the checkers
                piece = board[y][x]
                if piece == 'R':  # Red piece
                    pygame.draw.circle(screen, (255, 0, 0), (x * block_size + block_size // 2, y * block_size + block_size // 2), block_size // 2 - 5)
                elif piece == 'B':  # Black piece
                    pygame.draw.circle(screen, (0, 0, 0), (x * block_size + block_size // 2, y * block_size + block_size // 2), block_size // 2 - 5)

        pygame.display.flip()
    else:  # when not having pygame lib:
        for index, row in enumerate(board):
            print("  -" + "----"*8)
            r_print = f"{len(board)-index} |"
            for board_spot in row:
                r_print += f" {board_spot} |"
            print(r_print)
        print("  -" + "----"*8)
        print("   " + "".join([f" {chr(col+65)}  " for col in range(8)]))


def get_square(pos):
    block_size = window_size // 8
    x, y = pos
    return x // block_size, y // block_size


def decode_board_pos(r, c):
    """translate backend to human-readable board reading format"""
    return 8-r, chr(c+65)


def handle_click(pos, player_color: str, player_direction: int):
    global selected_piece, possible_moves
    x, y = get_square(pos)
    if selected_piece is None:  # Select a piece
        if board[y][x] == 'R':  # Only allow red pieces to be selected
            selected_piece = (y, x)
            possible_moves = checkers_bot_logic.get_valid_moves(board, player_color, player_direction)  # Get valid moves
    else:  # Move the selected piece
        start_row, start_col = selected_piece
        if (y, x) in [(move[2], move[3]) for move in possible_moves if move[0] == start_row and move[1] == start_col]:
            move_piece(start_row, start_col, y, x)
        selected_piece = None
        possible_moves = []


def move_piece(start_row, start_col, end_row, end_col):
    global possible_moves
    if tuple([start_row, start_col, end_row, end_col]) in possible_moves:
        board[end_row][end_col] = board[start_row][start_col]
        board[start_row][start_col] = ' '  # Clear the starting position
    draw_board()


def show_available():
    if possible_moves:
        for move in possible_moves:
            board[move[2]][move[3]] = "G"
    if not pygame:
        all_moves_printed = []
        for move in possible_moves:
            all_moves_printed.append(f"{move[0]}{chr(move[1]+65)} -> {move[2]}{chr(move[3]+65)}")


def main():
    global possible_moves, defending_color, current_color, player_direction
    running = True
    if pygame:
        while running:
            draw_board()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    handle_click(event.pos, current_color)

        pygame.quit()
    else:
        while running:
            draw_board()
            inp = input("What is your decision? >")
            if inp in ["Q", "q", "quit", "Quit"]:
                running = False
            if inp in ["show avaliable", "A"]:
                possible_moves = checkers_bot_logic.get_valid_moves(board, current_color, player_direction)
                print(possible_moves)
                show_available()
            if inp in ["Move", "M"]:
                print("moved")
                defending_color, current_color = current_color, defending_color
                if current_color == "R":
                    player_direction = -1
                else:
                    player_direction = 1


if __name__ == "__main__":
    main()
