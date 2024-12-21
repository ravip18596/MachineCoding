package main

import (
	"fmt"
	"math/rand"
	"time"
)

// Constants for game parameters
const (
	NumPlayers = 4
	DiceSides  = 6
	HomeBase   = 0
	WinningPos = 57 // Number of tiles to win
)

// Player struct
type Player struct {
	ID     int
	Name   string
	Pieces [4]int // Position of each piece on the board
	HasWon bool
}

// Game struct
type Game struct {
	Players []Player
	Board   []int // Represents the game board (not strictly needed for basic logic)
	Turn    int
}

// GameActions Interface for game actions (can be expanded)
type GameActions interface {
	RollDice() int
	MovePiece(player *Player, pieceIndex int, steps int)
	CheckWin(player *Player) bool
	NextTurn()
}

// RollDice Implements GameActions interface
func (g *Game) RollDice() int {
	rand.Seed(time.Now().UnixNano())
	return rand.Intn(DiceSides) + 1
}

func (g *Game) MovePiece(player *Player, pieceIndex int, steps int) {
	currentPos := player.Pieces[pieceIndex]
	newPos := currentPos + steps

	// Handle entering home stretch
	if currentPos < 52 && newPos >= 52 {
		remainingSteps := newPos - 52
		player.Pieces[pieceIndex] = 52 + remainingSteps // Adjust for home stretch
	} else if newPos < WinningPos {
		player.Pieces[pieceIndex] = newPos
	} else if newPos == WinningPos {
		player.Pieces[pieceIndex] = newPos
	} else {
		// If it goes past winning position, it bounces back
		overshot := newPos - WinningPos
		player.Pieces[pieceIndex] = WinningPos - overshot
	}
}

func (g *Game) CheckWin(player *Player) bool {
	for _, pos := range player.Pieces {
		if pos != WinningPos {
			return false
		}
	}
	player.HasWon = true
	return true
}

func (g *Game) NextTurn() {
	g.Turn = (g.Turn + 1) % NumPlayers
}

func main() {
	game := Game{
		Players: make([]Player, NumPlayers),
		Board:   make([]int, WinningPos+1), // Initialize the board
		Turn:    0,
	}

	// Initialize players
	for i := 0; i < NumPlayers; i++ {
		game.Players[i] = Player{ID: i, Name: fmt.Sprintf("Player %d", i)}
		for j := 0; j < 4; j++ {
			game.Players[i].Pieces[j] = HomeBase // Start at home base
		}
	}

	// Basic game loop (very simplified)
	for !game.Players[0].HasWon && !game.Players[1].HasWon && !game.Players[2].HasWon && !game.Players[3].HasWon {
		currentPlayer := &game.Players[game.Turn]
		fmt.Printf("%s's turn:\n", currentPlayer.Name)

		diceRoll := game.RollDice()
		fmt.Printf("Rolled a %d\n", diceRoll)

		// Very basic piece movement (needs more logic for selecting pieces etc.)
		game.MovePiece(currentPlayer, 0, diceRoll) // Moves the first piece for now
		fmt.Printf("%s's piece 0 is now at position %d\n", currentPlayer.Name, currentPlayer.Pieces[0])

		if game.CheckWin(currentPlayer) {
			fmt.Printf("%s has won!\n", currentPlayer.Name)
			break
		}

		game.NextTurn()
	}
}
