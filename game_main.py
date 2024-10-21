from typing import Literal

try:
    import pygame
except ImportError:
    pygame = None

from game_visualization import GameEngine
from game_logic import CheckersGame


class Game:
    def __init__(self, g_type: Literal['pygame', 'console'] = 'console'):
        self.g_type = g_type
        self.game_interaction_engine = GameEngine(vis_type=g_type)
        self.game_rulesystem = CheckersGame()
        self.running = False

    def pyg_main(self):
        """Main game loop for Pygame players"""
        self.running = True
        pygame.init()
        while self.running:
            self.game_interaction_engine.pyg_draw_board(self.game_rulesystem.board)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.game_interaction_engine.pyg_handle_click_select_piece(
                        event.pos,
                        self.game_rulesystem.current_player,
                        self.game_rulesystem.current_player_direction,
                        self.game_rulesystem.board,
                        self.game_rulesystem.poss
                    )

        pygame.quit()

    def c_main(self):
        """Main game loop for console players"""
        self.running = True
        while self.running:
            self.game_interaction_engine.pyg_draw_board(self.game_rulesystem.board)
            inp = input("What is your decision? > ")
            if inp.lower() in ["q", "quit"]:
                self.running = False
            elif inp in ["show available", "A"]:
                possible_moves = self.game_rulesystem.calculate_current_valid_moves()
                print("Available moves:", possible_moves)
                self.game_rulesystem.mark_available()
            elif inp in ["move", "M"]:
                # Implement logic for making a move
                print("Enter your move coordinates: ")
                move_coords = input()  # Example: "1,2 to 3,4"
                # You would need to parse this input and validate the move
                print("moved")

    def main(self):
        if self.g_type == "pygame":
            self.pyg_main()
        else:
            self.c_main()


if __name__ == '__main__':
    g_type = input("Choose game type (pygame/console): ").strip().lower()
    new_game = Game(g_type if g_type in ["pygame", "console"] else "console")
    new_game.main()
