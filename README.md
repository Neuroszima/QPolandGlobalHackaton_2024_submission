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

youtube link to submission presentation: https://youtu.be/fJQyK3DR-xs

## Running the project

Lets quickly mention how we can run the project. First however, a caveat:

**You need python 3.10 to run this project**

This is because we use pygame in version `2.1.0` which, after package managing got changed in `python 3.12` is not 
compatible with project requirements. All other requirements should be ok, but this package breaks. You are on your 
own when running this project with `py3.11+`.

Create a virtual environment and invoke:

```
(my_project_env) C:\project\directory\> python --version

Python 3.10.XX

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

## Inside the quantum brain

Grover algorithm, implemented for this project, resembles heavily implementations based on quantum counting, like the 
one used the problem of 2-Cut graph coloring. 

We first have to calculate correct number of qubits to use, when expressing all the possible states of the board. 
We use a rough estimate of: `floor(log2(valid_moves_count))+1` with the minimum number of qubits used as 1. This 
equation actually overshoots and reserves extra qubit on exact numbers: `4, 8, 16, 32 ...`, however this extra 
qubit is one of the advantageous tricks that we will explain now. We also extend the register by num of qubits 
equal to the number of conditions, that we will explain later.

### diluting solution space

In total we reserve `floor(log2(valid_moves_count))+1  + num_of_conditions  + 2`. We reserve this much, because we are 
aware of how Grover's algorithm work. This way we artificially pump the Omega, which is the total number of quantum 
states, that are checked inside the algorithm. This isn't the resource optimization and it doesn't try to be one. 
Optimal solution would use only exact number of qubits that are enough to encode all the possible solutions. We use 
this however, to avoid problems with inversion over the mean.

Because what happens if exactly half or very close to half of your entire searched space are the solutions? Grover's
algorithm becomes useless; inversion over the mean stops working, as when you flag half the states as "negative" and the
others are "positive", the mean becomes zero and inversion does not improve any of these probabilities. Meanwhile, when
we artificially pump the number of states by 2x (1 qubit added), when exactly half of our original space is taken by
correct solutions, Grover's will work at full force. The only thing that we should account for, is that, when marking 
the states, we only mark from one half of the omega (for example, we check all the solutions, with 
"most significant bit" being `1`)

Artificial solution pumping has also an added benefit of preventing "probability overshoot".

When applying grovers algorithm, it is common to use several "iterations" to boost probability of true solutions up,
especially if they only consist a small portion of total amount of states (for example 0.1%). However we don't 
exactly know how many solutions are there in the space. We could use Shor's to judge that, but my knowledge is limited,
and I did not want to spend days researching the improvement that could fail in the end, which would fail the project.

Instead, we know this: when applied several times, eventually situation "reverts". The probabilities of solutions 
encoded in initialization, start to drop, and eventually die out, while incorrect answers will dominate. However, we are
able to 100% prevent this, by diluting state space, and limit ourselves to fixed amount of iterations. Implementing 
algorithm this way, it is **mathematically impossible to overshoot**, when picked proper number of diffusion iterations
and proper amount of qubits. That is why we extend the register further, by `num_of_conditions`, because per amount of
conditions, when many of them are triggered, we want to diffuse over combinations of these:
```
1+ conditon fulfilled
2+ conditions fulfilled
3 conditions fulfilled
```
When done like this, we can really make a diverse quantum state.

If you think about it long enough, and you will think about the "more than 1 condition fulfilled" and such, you will
start to realize that we actually developed something resembling quantum perceptron.

### "greater than" condition 

Ok but how do we select states? We do very simple thing of just having enough 
