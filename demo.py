# demo.py
import pygame
from game_logic import CheckersGame

class CheckersVisualizer:
    def __init__(self):
        self.game = CheckersGame()
        self.window_size = 600
        self.screen = None
        self.running = True

        if pygame:
            pygame.init()
            self.screen = pygame.display.set_mode((self.window_size, self.window_size))
            pygame.display.set_caption("Checkers Game")

    def draw_board(self):
        block_size = self.window_size // 8  # Checkers board is 8x8
        for y in range(8):
            for x in range(8):
                rect = pygame.Rect(x * block_size, y * block_size, block_size, block_size)
                color = (255, 255, 255) if (x + y) % 2 == 0 else (0, 0, 0)
                pygame.draw.rect(self.screen, color, rect)

                # Draw the checkers
                piece = self.game.board[y][x]
                if piece == 'R':  # Red piece
                    pygame.draw.circle(self.screen, (255, 0, 0), (x * block_size + block_size // 2, y * block_size + block_size // 2), block_size // 2 - 5)
                elif piece == 'B':  # Black piece
                    pygame.draw.circle(self.screen, (0, 0, 0), (x * block_size + block_size // 2, y * block_size + block_size // 2), block_size // 2 - 5)
                elif piece == "G":  # Available move indicator
                    pygame.draw.circle(self.screen, (0, 255, 0), (x * block_size + block_size // 2, y * block_size + block_size // 2), block_size // 2 - 5)

        pygame.display.flip()

    def get_square(self, pos):
        block_size = self.window_size // 8
        x, y = pos
        return x // block_size, y // block_size

    def handle_click(self, pos):
        x, y = self.get_square(pos)
        if self.game.valid_moves:
            for move in self.game.valid_moves:
                if (y, x) == (move[2], move[3]):
                    self.game.execute_move(move[0], move[1], move[2], move[3])
                    break
        self.draw_board()

    def run(self):
        while self.running:
            self.draw_board()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

        pygame.quit()

if __name__ == "__main__":
    visualizer = CheckersVisualizer()
    visualizer.run()