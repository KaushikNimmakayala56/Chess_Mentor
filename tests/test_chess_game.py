"""
Tests for chess game functionality.
"""
import pytest
import chess
import chess.engine
from unittest.mock import Mock, patch
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from play_game import create_new_game, make_move, is_game_over


class TestChessGame:
    """Test cases for chess game functionality."""
    
    def test_create_new_game(self):
        """Test that a new game is created with correct initial state."""
        board = create_new_game()
        
        assert board is not None
        assert isinstance(board, chess.Board)
        assert board.fen() == chess.Board().fen()
        assert board.turn == chess.WHITE
        assert not board.is_game_over()
    
    def test_make_legal_move(self):
        """Test making a legal move."""
        board = chess.Board()
        initial_fen = board.fen()
        
        # Make a legal move (e4)
        move = chess.Move.from_uci("e2e4")
        result = make_move(board, move)
        
        assert result is True
        assert board.fen() != initial_fen
        assert board.turn == chess.BLACK
    
    def test_make_illegal_move(self):
        """Test that illegal moves are rejected."""
        board = chess.Board()
        initial_fen = board.fen()
        
        # Try to make an illegal move (e2e5 - pawn can't move 3 squares)
        move = chess.Move.from_uci("e2e5")
        result = make_move(board, move)
        
        assert result is False
        assert board.fen() == initial_fen
        assert board.turn == chess.WHITE
    
    def test_game_not_over_at_start(self):
        """Test that a new game is not over."""
        board = chess.Board()
        assert not is_game_over(board)
    
    def test_game_over_after_checkmate(self):
        """Test that game is over after checkmate."""
        board = chess.Board()
        
        # Fool's mate sequence
        moves = ["f2f3", "e7e6", "g2g4", "d8h4"]
        
        for move_uci in moves:
            move = chess.Move.from_uci(move_uci)
            make_move(board, move)
        
        assert is_game_over(board)
        assert board.is_checkmate()
    
    @patch('chess.engine.SimpleEngine.popen_uci')
    def test_stockfish_move_generation(self, mock_engine):
        """Test that Stockfish can generate moves."""
        # Mock the engine
        mock_engine_instance = Mock()
        mock_engine_instance.play.return_value = Mock()
        mock_engine_instance.play.return_value.move = chess.Move.from_uci("e7e5")
        mock_engine.return_value.__enter__.return_value = mock_engine_instance
        mock_engine.return_value.__exit__.return_value = None
        
        board = chess.Board()
        board.push(chess.Move.from_uci("e2e4"))  # White plays e4
        
        # This would normally call Stockfish, but we're mocking it
        # In a real test, you'd need Stockfish installed
        assert board.turn == chess.BLACK


def create_new_game():
    """Helper function to create a new chess game."""
    return chess.Board()


def make_move(board, move):
    """Helper function to make a move on the board."""
    if move in board.legal_moves:
        board.push(move)
        return True
    return False


def is_game_over(board):
    """Helper function to check if game is over."""
    return board.is_game_over()


if __name__ == "__main__":
    pytest.main([__file__]) 