from typing import Literal

try:
    import pygame
except ImportError:
    pygame = None

from game_visualization import GameDisplayEngine
from game_logic import CheckersGame
from bot_logic import QuantumBot


class Game:
    def __init__(self, g_type: Literal['pygame', 'console'] | str | None = None):
        self.g_type = g_type if g_type else "pygame"
        self.game_interaction_engine = GameDisplayEngine(vis_type=g_type)
        self.game_rulesystem = CheckersGame()
        self.q_bot = QuantumBot(3)

        # we update the bot to be an enemy of human player
        # the "current" is from bot perspective as a "main character" :)
        self.q_bot.update_current_player_info(
            current_player=self.game_rulesystem.STARTING_ENEMY,
            current_enemy_player=self.game_rulesystem.STARTING_PLAYER,
            current_player_direction=self.game_rulesystem.PLAYER_BOARD_DIRECTION[
                self.game_rulesystem.STARTING_ENEMY]
        )

        self.running = False
        self.turn_start = True

    def end_turn_cleanup(self):
        """all the minor cleanup procedures"""
        # WHEN LEFT - GREEN HINT MARKS ON BOARD (sa "G" character) INTERFERE WITH (" ") CHECKS!
        # TO CLEAN UP!!!
        # FOLLOWING IS BARELY MINIMUM!!! NEED MORE CAREFUL!!!
        self.game_rulesystem.clean_hints()
        self.game_rulesystem.switch_player()
        self.game_rulesystem.selected_piece = None
        self.game_rulesystem.hints_for_selection = None
        self.turn_start = True  # for all "next turn" actions to be triggered

    def bot_move(self):
        """execute chain of events that bot does"""
        # we execute bot controls and movements -> black pieces
        self.q_bot.calculate_recommendations(
            self.game_rulesystem.valid_moves,
            self.game_rulesystem.board
        )
        self.q_bot.parse_recommendations_human_readable()
        self.game_interaction_engine.pyg_draw_quantum_states(self.q_bot.human_readable_predictions)
        best_moves = self.q_bot.parse_recommendations_bot_use()
        to_execute = best_moves[0][0]  # top of the list and 0 column (move)
        self.game_rulesystem.execute_move(*to_execute)
        self.end_turn_cleanup()

    def pyg_main(self):
        """Main game loop for Pygame players"""
        self.running = True
        pygame.init()

        while self.running:
            self.game_interaction_engine.pyg_draw_board(
                self.game_rulesystem.board,
                self.game_rulesystem.selected_piece,
                self.game_rulesystem.hints_for_selection
            )
            self.game_interaction_engine.pyg_draw_quantum_states(self.q_bot.human_readable_predictions)
            if self.turn_start:
                # this will make calculation only happen once
                self.game_rulesystem.calculate_current_valid_moves()
                self.game_rulesystem.check_lose_game()  # don't invert with ^ (above)
                self.turn_start = False

            if self.game_rulesystem.current_player == self.game_rulesystem.STARTING_PLAYER:
                # we serve events to control player decisions -> red pieces
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        event_coordinates, game_event = self.game_interaction_engine.pyg_handle_click(event.pos)
                        if game_event == "board":
                            if not self.game_rulesystem.selected_piece:
                                self.game_rulesystem.selected_piece = event_coordinates
                                self.game_rulesystem.calculate_hints_for_selection()
                            else:
                                # player decision
                                if event_coordinates in self.game_rulesystem.hints_for_selection:
                                    to_execute = (*self.game_rulesystem.selected_piece, *event_coordinates)
                                    self.game_rulesystem.execute_move(*to_execute)
                                    self.end_turn_cleanup()
                                else:
                                    self.game_rulesystem.selected_piece = None
                                    self.game_rulesystem.hints_for_selection = None
            else:
                self.bot_move()

            pygame.display.flip()
            
               # Check for win or lose conditions
        if self.game_rulesystem.check_win_condition():
            self.game_interaction_engine.pyg_draw_win_lose_message("You Win!")
            pygame.time.delay(3000)  # Pause for 3 seconds before closing
            self.running = False
        elif self.game_rulesystem.check_lose_condition():
            self.game_interaction_engine.pyg_draw_win_lose_message("You Lose!")
            pygame.time.delay(3000)  # Pause for 3 seconds before closing
            self.running = False


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

