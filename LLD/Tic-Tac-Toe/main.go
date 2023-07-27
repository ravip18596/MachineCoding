package main

import (
	"fmt"
	"strconv"
	"strings"
)

type PieceType string

const (
	X PieceType = "X"
	O PieceType = "O"
	E PieceType = "E"
)

type Player struct {
	name         string
	playingPiece PieceType
}

type Board struct {
	size  int
	board [][]PieceType
}

func ConstructBoard(size int) *Board {
	gameBoard := make([][]PieceType, size)
	for i := 0; i < size; i++ {
		gameBoard[i] = make([]PieceType, size)
		for j := 0; j < size; j++ {
			gameBoard[i][j] = E
		}
	}
	return &Board{
		size:  size,
		board: gameBoard,
	}
}

func (b *Board) printBoard() {
	for i := 0; i < b.size; i++ {
		for j := 0; j < b.size; j++ {
			if b.board[i][j] == E {
				fmt.Print("  ")
			} else {
				fmt.Print(b.board[i][j] + "  ")
			}
			fmt.Print(" | ")
		}
		fmt.Println()
	}
}

func (b *Board) addPiece(row, col int, pieceType PieceType) bool {
	if b.board[row][col] != E {
		return false
	}
	b.board[row][col] = pieceType
	return true
}

type TicTacToeGame struct {
	gameBoard *Board
	players   []Player
}

func initialiseGame() *TicTacToeGame {
	player1 := Player{
		name:         "Player 1",
		playingPiece: X,
	}
	player2 := Player{
		name:         "Player 2",
		playingPiece: O,
	}

	board := ConstructBoard(3)
	game := TicTacToeGame{
		players:   []Player{player1, player2},
		gameBoard: board,
	}
	return &game
}

func (t *TicTacToeGame) startGame() string {
	noWinner := true
	for noWinner {
		playerTurn := t.players[0]
		t.players = t.players[1:]

		t.gameBoard.printBoard()
		fmt.Println("Player: ", playerTurn.name, " Enter row, column: ")
		var line string
		fmt.Scanln(&line)
		split := strings.Split(line, ",")
		row, _ := strconv.Atoi(strings.TrimSpace(split[0]))
		col, _ := strconv.Atoi(strings.TrimSpace(split[1]))

		pieceAddedSuccessfully := t.gameBoard.addPiece(row, col, playerTurn.playingPiece)
		if !pieceAddedSuccessfully {
			fmt.Println("Incorrect position chosen, try again")
			// Add current player at the front
			t.players = append([]Player{playerTurn}, t.players...)
			continue
		}
		// Add current player at the end
		t.players = append(t.players, playerTurn)
		winner := t.isThereWinner(row, col, playerTurn.playingPiece)
		if winner {
			return playerTurn.name
		}
	}
	return "tie"
}

func (t *TicTacToeGame) isThereWinner(row, col int, playingPiece PieceType) bool {
	rowWinner := true
	colWinner := true
	diagonalWinner := true
	antiDiagonalWinner := true

	for i := 0; i < t.gameBoard.size; i++ {
		if t.gameBoard.board[row][i] == E || t.gameBoard.board[row][i] != playingPiece {
			rowWinner = false
		}
	}

	for i := 0; i < t.gameBoard.size; i++ {
		if t.gameBoard.board[i][col] == E || t.gameBoard.board[i][col] != playingPiece {
			colWinner = false
		}
	}

	for i, j := 0, 0; i < t.gameBoard.size; i, j = i+1, j+1 {
		if t.gameBoard.board[i][j] == E || t.gameBoard.board[i][j] != playingPiece {
			diagonalWinner = false
		}
	}

	for i, j := 0, t.gameBoard.size-1; i < t.gameBoard.size; i, j = i+1, j-1 {
		if t.gameBoard.board[i][j] == E || t.gameBoard.board[i][j] != playingPiece {
			antiDiagonalWinner = false
		}
	}

	return rowWinner || colWinner || diagonalWinner || antiDiagonalWinner
}

func main() {
	game := initialiseGame()
	winner := game.startGame()
	fmt.Println("the winner is ", winner)
}
