# QPoland Global Hackathon 2024 submission

Quantronix team's submission to Open track for QPoland Global Quantum Hackaton 2024 organized on DoraHacks


## About project

This project showcases the use of quantum computing in gaming, by generating suggestions for non-playable-characters, 
like a game bots. Here we mimic the suggestion from so called recommendation engines, that are very popular in chess

In terms of the game itself, we chose <b>checkers</b> as our target game. It is far easier to implement than chess,
in a time and human resources constraint of this hackathon. We still **did not implement all the features** of checkers
namely we miss:

- king mechanic - when you reach end of the board, in regular game in real life, you "flip the piece" and it starts
    to have a power of going whatever diagonal direction it can (with regular pieces you can not move backwards)
- tournament rules of multi-beating pieces - when you beat an opponents piece, you can keep going and keep beating, as 
    long as you have something to jump over

In terms of high overview of the project, basic information about different modules in this projects is contained in
the Youtube video attached to the submission.

## Running the project

Lets quickly mention how we can run the project. First however, a caveat:

#### You need python 3.10 to run this project

This is because we use pygame in version `2.1.0` which, after package managing got changed in `python 3.12` is not 
compatible with project requirements. All other requirements should be ok, but this package breaks. You are on your 
own when running this project with `py3.12`.

Create a virtual environment and invoke:

```
(my_project_env) C:\project\directory\> python --version

Python 3.10.8

(my_project_env) C:\project\directory\> pip install -r requirements.txt
```

after installation is complete, to run the game, invoke:

```
(my_project_env) C:\project\directory\> python demo.py
```

to run the game.

## High level project overview

In short, visualization package is responsible for running the game visuals and updating representation of the board
for the player to see, as well as handling clicking buttons (like 'Play again') + showing quantum states with 
probabilities. These probabilities are shown as "predictions of all the bot moves" from last turn. You can also see in
orange, which move did the bot decide to take, both at "quantum probabilities" sidebar, and on the board.

game_logic is where we keep everything tied to board situation, checking valid moves, executing the move etc. It also
generate hints and keeps info of selected piece, to execute the move from its perspective

game_main has the main game loop and all functions responsible for drawing window elements are invoked there. We stuck
to doing simple single game loop for simplicity. There is also function that invoke series of calculations, 
that the bot does, with board update after bot move.

finally there is bot_logic, which contains all the quantum sweetness you are here for... **RIGHT?!**

