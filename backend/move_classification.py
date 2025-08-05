"""
Chess move classification module.
Contains logic for classifying moves and generating feedback messages using Chess.com-style CPL thresholds.
"""

import chess

# Piece values for material calculation (kept for potential future use)
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

def classify_move(cpl):
    """
    Classify a move based on Centipawn Loss (CPL) using Chess.com-style thresholds.
    
    Args:
        cpl (int): Centipawn loss compared to the best move
    
    Returns:
        str: Move classification - one of:
             'brilliant', 'best', 'excellent', 'good', 'book', 'inaccuracy', 'mistake', 'blunder'
    """
    if cpl == 0:
        # TODO: Add logic to distinguish "brilliant" from "best" moves
        # For now, treat all 0 CPL moves as "best"
        return 'best'
    elif 1 <= cpl <= 20:
        return 'excellent'
    elif 21 <= cpl <= 50:
        return 'good'
    elif 51 <= cpl <= 100:
        return 'inaccuracy'
    elif 101 <= cpl <= 300:
        return 'mistake'
    else:  # cpl >= 301
        return 'blunder'

def generate_feedback_message(classification, cpl, user_move, best_move):
    """
    Generate feedback message based on Chess.com-style move classification.
    
    Args:
        classification (str): Move classification from classify_move()
        cpl (int): Centipawn loss value
        user_move (str): The move played by the user (in SAN notation)
        best_move (str): The best move according to the engine (in SAN notation)
    
    Returns:
        str: Formatted feedback message
    """
    if classification == 'brilliant':
        return f"Your move {user_move}: Brilliant! ✨ (CPL: {cpl})"
    elif classification == 'best':
        return f"Your move {user_move}: Best Move! 🎯 (CPL: {cpl})"
    elif classification == 'excellent':
        return f"Your move {user_move}: Excellent! 💚 (CPL: {cpl})"
    elif classification == 'good':
        return f"Your move {user_move}: Good Move! 👍 (CPL: {cpl})"
    elif classification == 'book':
        # TODO: Implement book move detection
        return f"Your move {user_move}: Book Move! 📚 (CPL: {cpl})"
    elif classification == 'inaccuracy':
        return f"Your move {user_move}: Inaccuracy ⚠️ (CPL: {cpl}) - Best: {best_move}"
    elif classification == 'mistake':
        return f"Your move {user_move}: Mistake ❌ (CPL: {cpl}) - Best: {best_move}"
    elif classification == 'blunder':
        return f"Your move {user_move}: Blunder! 💥 (CPL: {cpl}) - Best: {best_move}"
    else:
        # Fallback
        return f"Your move {user_move}: Move analyzed (CPL: {cpl})"