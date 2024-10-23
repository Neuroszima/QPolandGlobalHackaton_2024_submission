# demo.py
from game_main import Game


if __name__ == '__main__':
    g_type = input("Choose game type (pygame/console): ").strip().lower()
    new_game = Game(g_type if g_type in ["pygame", "console"] else "console")
    new_game.main()
