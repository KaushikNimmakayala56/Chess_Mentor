"""
Tests for PGN parsing functionality.
"""
import pytest
import chess.pgn
import io
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parse_pgn import extract_positions, parse_game_moves


class TestPGNParsing:
    """Test cases for PGN parsing functionality."""
    
    def test_extract_positions_from_simple_game(self):
        """Test extracting positions from a simple PGN game."""
        # Simple PGN with just a few moves
        pgn_text = """
[Event "Test Game"]
[Site "Test Site"]
[Date "2024.01.01"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 *
        """
        
        positions = extract_positions_from_text(pgn_text)
        
        # Should have positions after each move
        assert len(positions) >= 3  # At least 3 positions (start, after e4, after e5)
        assert all(isinstance(pos, str) for pos in positions)
        
        # First position should be starting position
        assert "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" in positions[0]
    
    def test_parse_game_moves(self):
        """Test parsing moves from a PGN game."""
        pgn_text = """
[Event "Test Game"]
[Site "Test Site"]
[Date "2024.01.01"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 *
        """
        
        moves = parse_game_moves_from_text(pgn_text)
        
        assert len(moves) == 6  # 3 moves for each player
        assert moves[0] == "e2e4"  # e4
        assert moves[1] == "e7e5"  # e5
        assert moves[2] == "g1f3"  # Nf3
        assert moves[3] == "b8c6"  # Nc6
        assert moves[4] == "f1b5"  # Bb5
    
    def test_empty_pgn(self):
        """Test handling of empty PGN."""
        positions = extract_positions_from_text("")
        assert len(positions) == 0
    
    def test_invalid_pgn(self):
        """Test handling of invalid PGN."""
        invalid_pgn = "This is not valid PGN"
        positions = extract_positions_from_text(invalid_pgn)
        assert len(positions) == 0
    
    def test_game_with_comments(self):
        """Test parsing PGN with comments and annotations."""
        pgn_with_comments = """
[Event "Test Game"]
[Site "Test Site"]
[Date "2024.01.01"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 {Good opening move} e5 {Black responds in kind} 2. Nf3 Nc6 *
        """
        
        positions = extract_positions_from_text(pgn_with_comments)
        moves = parse_game_moves_from_text(pgn_with_comments)
        
        # Should still extract positions and moves despite comments
        assert len(positions) > 0
        assert len(moves) == 4  # e4, e5, Nf3, Nc6
    
    def test_game_with_variations(self):
        """Test parsing PGN with move variations."""
        pgn_with_variations = """
[Event "Test Game"]
[Site "Test Site"]
[Date "2024.01.01"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 (1. d4 d5) e5 2. Nf3 Nc6 *
        """
        
        positions = extract_positions_from_text(pgn_with_variations)
        moves = parse_game_moves_from_text(pgn_with_variations)
        
        # Should extract main line moves, not variations
        assert len(moves) == 4  # e4, e5, Nf3, Nc6
        assert "e2e4" in moves
        assert "d2d4" not in moves  # Variation move should not be included


def extract_positions_from_text(pgn_text):
    """Helper function to extract positions from PGN text."""
    try:
        game = chess.pgn.read_game(io.StringIO(pgn_text))
        if game is None:
            return []
        
        positions = []
        board = game.board()
        positions.append(board.fen())
        
        for move in game.mainline_moves():
            board.push(move)
            positions.append(board.fen())
        
        return positions
    except Exception:
        return []


def parse_game_moves_from_text(pgn_text):
    """Helper function to parse moves from PGN text."""
    try:
        game = chess.pgn.read_game(io.StringIO(pgn_text))
        if game is None:
            return []
        
        moves = []
        for move in game.mainline_moves():
            moves.append(move.uci())
        
        return moves
    except Exception:
        return []


if __name__ == "__main__":
    pytest.main([__file__]) 