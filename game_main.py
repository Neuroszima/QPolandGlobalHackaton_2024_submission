from typing import Literal

try:
    import pygame
except ImportError:
    pygame = None

from game_visualization import GameDisplayEngine
from game_logic import CheckersGame


class Game:
    def __init__(self, g_type: Literal['pygame', 'console'] = 'console'):
        self.g_type = g_type
        self.game_interaction_engine = GameDisplayEngine(vis_type=g_type)
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
                    # self.game_interaction_engine.pyg_handle_click_select_piece(event.pos)
                    move = self.game_interaction_engine.pyg_handle_click(
                        event.pos, self.game_rulesystem.valid_moves)
                    if move:
                        self.game_rulesystem.execute_move(*move)

            pygame.display.flip()

        pygame.quit()

    def c_main(self):
        """Main game loop for console players"""
        self.running = True
        while self.running:
            self.game_interaction_engine.c_draw_board(self.game_rulesystem.board)
            inp = input("What is your decision? (q, A, M) > ")
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

