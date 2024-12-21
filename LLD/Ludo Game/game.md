Explanation
-----------

Design Approach and Explanation:

1. Data Structures:

   1. Player: Stores player information (ID, name, piece positions, win status). The Pieces array holds the current position of each of the four pieces.
   2. Game: Holds game state (players, board, current turn). The Board is an integer slice of the game board.

2. Interfaces:
   1. GameActions: Defines the actions that can be performed in the game (rolling dice, moving pieces, checking for a win). This promotes good design by decoupling actions from the Game struct itself.

3. Game Logic:
   1. RollDice(): Generates a random number between 1 and 6.
   2. MovePiece(): Updates the position of a piece based on the dice roll. Includes basic logic for handling the home stretch (the last 6 steps) and bouncing back if a player overshoots the winning position.
   3. CheckWin(): Checks if a player has won by checking if all their pieces are at the winning position.
   4. NextTurn(): Cycles through the players.
   
4. Game Loop:
   The main function contains a basic game loop that continues until a player wins. It simulates turns, dice rolls, and piece movement.
