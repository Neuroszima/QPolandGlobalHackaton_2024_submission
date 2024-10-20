import pygame
import checkers_bot_logic

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

selected_piece = None
possible_moves = []

def draw_board():
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

def get_square(pos):
    block_size = window_size // 8
    x, y = pos
    return x // block_size, y // block_size

def handle_click(pos):
    global selected_piece, possible_moves
    x, y = get_square(pos)
    if selected_piece is None:  # Select a piece
        if board[y][x] == 'R':  # Only allow red pieces to be selected
            selected_piece = (y, x)
            possible_moves = checkers_bot_logic.get_valid_moves(board)  # Get valid moves
    else:  # Move the selected piece
        start_row, start_col = selected_piece
        if (y, x) in [(move[2], move[3]) for move in possible_moves if move[0] == start_row and move[1] == start_col]:
            move_piece(start_row, start_col, y, x)
        selected_piece = None
        possible_moves = []

def move_piece(start_row, start_col, end_row, end_col):
    board[end_row][end_col] = board[start_row][start_col]
    board[start_row][start_col] = ' '  # Clear the starting position
    draw_board()

def main():
    running = True
    while running:
        draw_board()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(event.pos)

    pygame.quit()

if __name__ == "__main__":
    main()
