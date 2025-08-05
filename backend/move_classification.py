"""
Chess move classification module.
Contains logic for classifying moves and generating feedback messages.
"""

import chess

# Piece values for material calculation
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

def classify_move(material_change, positional_change):
    """
    Classify a move based on material and positional changes.
    
    Args:
        material_change (int): Change in material value (positive = gain, negative = loss)
        positional_change (int): Change in positional evaluation (positive = better, negative = worse)
    
    Returns:
        tuple: (classification, priority) where classification is one of:
               'excellent', 'good', 'okay', 'inaccuracy', 'blunder'
               and priority is 'material' or 'positional'
    """
    # Material loss is always bad
    if material_change < -50:
        if material_change < -200:
            return 'blunder', 'material'
        else:
            return 'inaccuracy', 'material'
    
    # Material gain is always good
    elif material_change > 50:
        if material_change > 200:
            return 'excellent', 'material'
        else:
            return 'good', 'material'
    
    # No material change, evaluate by position
    else:
        if positional_change > 200:
            return 'excellent', 'positional'
        elif positional_change > 50:
            return 'good', 'positional'
        elif positional_change > -50:
            return 'okay', 'positional'
        elif positional_change > -200:
            return 'inaccuracy', 'positional'
        else:
            return 'blunder', 'positional'

def generate_feedback_message(classification, priority, material_change, positional_change, user_move, best_move):
    """
    Generate feedback message based on move classification.
    
    Args:
        classification (str): Move classification ('excellent', 'good', 'okay', 'inaccuracy', 'blunder')
        priority (str): Whether evaluation is based on 'material' or 'positional'
        material_change (int): Change in material value
        positional_change (int): Change in positional evaluation
        user_move (str): The move played by the user (in SAN notation)
        best_move (str): The best move according to the engine (in SAN notation)
    
    Returns:
        str: Formatted feedback message
    """
    # Material-based feedback
    if priority == 'material':
        if classification == 'blunder':
            return f"Your move {user_move}: Blunder! You lost material (-{abs(material_change)/100:.1f}) (Best: {best_move})"
        elif classification == 'inaccuracy':
            return f"Your move {user_move}: Inaccuracy. You lost material (-{abs(material_change)/100:.1f}) (Best: {best_move})"
        elif classification == 'good':
            return f"Your move {user_move}: Good move! You won material (+{material_change/100:.1f})"
        elif classification == 'excellent':
            return f"Your move {user_move}: Excellent! You won material (+{material_change/100:.1f})"
    
    # Positional-based feedback
    else:  # priority == 'positional'
        if classification == 'blunder':
            return f"Your move {user_move}: Blunder! {positional_change/100:.1f} (Best: {best_move})"
        elif classification == 'inaccuracy':
            return f"Your move {user_move}: Inaccuracy. {positional_change/100:.1f} (Best: {best_move})"
        elif classification == 'okay':
            return f"Your move {user_move}: Okay move. {positional_change/100:.1f}"
        elif classification == 'good':
            return f"Your move {user_move}: Good move! +{positional_change/100:.1f}"
        elif classification == 'excellent':
            return f"Your move {user_move}: Excellent! +{positional_change/100:.1f}"
    
    # Fallback (should never reach here)
    return f"Your move {user_move}: Move analyzed."