"""
Chess Opening Database Module

This module contains a comprehensive database of popular chess openings
and helper functions for book move detection and opening identification.
"""

import chess
import chess.pgn
from typing import Optional, Dict, List


# Chess Opening Database
OPENINGS = [
    {
        "eco": "A00",
        "name": "King's Pawn Opening",
        "moves": ["e4"],
        "description": "One of the most popular first moves in chess, immediately controlling the center and opening lines for the queen and bishop."
    },
    {
        "eco": "A40",
        "name": "Queen's Pawn Opening",
        "moves": ["d4"],
        "description": "Controls the center and opens lines for the queen and bishop, often leading to rich positional play."
    },
    {
        "eco": "A01",
        "name": "Nf3 Opening (Reti)",
        "moves": ["Nf3"],
        "description": "A flexible opening that can transpose into many systems, avoiding early commitment to pawn structure."
    },
    {
        "eco": "A20",
        "name": "English Opening (One Move)",
        "moves": ["c4"],
        "description": "Controls the center from the flank and prepares to develop pieces harmoniously."
    },
    {
        "eco": "B00",
        "name": "e3 Opening (Van't Kruijs)",
        "moves": ["e3"],
        "description": "A quiet and flexible start, often leading to Colle or reversed French structures."
    },
    {
        "eco": "B20",
        "name": "Sicilian Defense (One Move)",
        "moves": ["e4", "c5"],
        "description": "The most popular defense to 1.e4, creating unbalanced positions and counterattacking chances."
    },
    {
        "eco": "C00",
        "name": "French Defense (One Move)",
        "moves": ["e4", "e6"],
        "description": "Prepares to challenge the center with ...d5, often leading to closed pawn structures."
    },
    {
        "eco": "B10",
        "name": "Caro-Kann Defense (One Move)",
        "moves": ["e4", "c6"],
        "description": "A solid defense aiming for a strong pawn structure and long-term safety."
    },
    {
        "eco": "B07",
        "name": "Pirc Defense (One Move)",
        "moves": ["e4", "d6"],
        "description": "A hypermodern setup allowing White to occupy the center before counterattacking."
    },
    {
        "eco": "B01",
        "name": "Scandinavian Defense (One Move)",
        "moves": ["e4", "d5"],
        "description": "Immediately challenges White's center, leading to open and tactical play."
    },
    {
        "eco": "C60",
        "name": "Ruy Lopez",
        "moves": ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4"],
        "description": "White develops actively and pressures the e5 pawn; after ...a6 Ba4, Black fights for the center while White keeps the pin."
    },
    # Bongcloud Attack - A provocative and highly unconventional opening where the King is moved early to challenge traditional principles.
    {
        "eco": "C20",
        "name": "Bongcloud Attack",
        "moves": ["e4", "e5", "Ke2", "Nf6", "Ke3"],
        "description": "A provocative and highly unconventional line where White walks the king to e3 very early."
    },
    # Najdorf Variation - Black prepares to seize central control with the move ...e5, while keeping the position flexible and dynamic.
    {
        "eco": "B90",
        "name": "Najdorf Variation",
        "moves": ["e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Nf6", "Nc3", "a6", "Be2", "e5"],
        "description": "A flagship Sicilian line; ...a6 prevents Nb5 and supports ...e5 or ...b5 for rich, dynamic play."
    },
    # Berlin Defense - Black challenges White's center and aims for a balanced, simplified endgame with equal chances.
    {
        "eco": "C65",
        "name": "Berlin Defense",
        "moves": ["e4", "e5", "Nf3", "Nc6", "Bb5", "Nf6", "O-O", "Nxe4", "Re1", "Nd6"],
        "description": "A rock-solid defense often leading to simplified positions and balanced endgames."
    },
    # King's Indian Defense - Black allows White to build a large central pawn presence, with the plan of undermining and attacking it with pieces.
    {
        "eco": "E60",
        "name": "King's Indian Defense",
        "moves": ["d4", "Nf6", "c4", "g6", "Nc3", "Bg7", "e4", "d6"],
        "description": "Hypermodern strategy: concede the center temporarily, then strike with ...e5 or ...c5 and a kingside attack."
    },
    # Queen's Gambit - White challenges Black's center and aims to control the light squares, while Black defends the d5 pawn.
    {
        "eco": "D30",
        "name": "Queen's Gambit",
        "moves": ["d4", "d5", "c4", "e6", "Nc3", "Nf6"],
        "description": "White offers a wing pawn to deflect Black's d-pawn and claim central space."
    },
    # Italian Game - White prepares to build a strong pawn center with c3 and d4, while both sides develop pieces rapidly.
    {
        "eco": "C53",
        "name": "Italian Game",
        "moves": ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "c3", "Nf6"],
        "description": "Classical development and control of the center; plans often include d4 or a kingside attack."
    },
    # Sicilian Defense - Black immediately creates an unbalanced position and gains a semi-open c-file, while White develops a lead in central control.
    {
        "eco": "B50",
        "name": "Sicilian Defense",
        "moves": ["e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Nf6"],
        "description": "Creates imbalanced positions; Black fights for counterplay on the c-file and dark squares."
    },
    # London System - White develops pieces in a solid, consistent manner that is less sensitive to Black's responses.
    {
        "eco": "D02",
        "name": "London System",
        "moves": ["d4", "d5", "Nf3", "Nf6", "Bf4", "e6", "e3", "Nbd7"],
        "description": "Solid, system-based development with Bf4; resilient against a wide range of setups."
    },
    # Fool's Mate - Fastest possible checkmate in chess from opening blunders.
    {
        "eco": "A02",
        "name": "Fool's Mate",
        "moves": ["f3", "e5", "g4", "Qh4#"],
        "description": "The fastest checkmate in chess when White weakens the kingside fatally."
    },
    # English Opening - A flank opening where White controls the center from the side.
    {
        "eco": "A25",
        "name": "English Opening",
        "moves": ["c4", "e5", "Nc3", "Nf6", "g3", "d5"],
        "description": "Controls the center from the flank; flexible structures and frequent transpositions."
    },
    # Dutch Defense - An aggressive opening where Black fights for control of e4 square.
    {
        "eco": "A85",
        "name": "Dutch Defense",
        "moves": ["d4", "f5", "c4", "Nf6", "g3", "g6", "Bg2"],
        "description": "Seeks control of e4 and dynamic kingside play with ...f5."
    },
    # King's Gambit - White sacrifices a pawn for rapid development and an open f-file.
    {
        "eco": "C30",
        "name": "King's Gambit",
        "moves": ["e4", "e5", "f4", "exf4", "Nf3", "g5"],
        "description": "Romantic pawn sacrifice for rapid development and open lines to the king."
    },
    # Grünfeld Defense - Black challenges White's center with pieces after allowing central pawns.
    {
        "eco": "D70",
        "name": "Grünfeld Defense",
        "moves": ["d4", "Nf6", "c4", "g6", "Nc3", "d5", "cxd5", "Nxd5"],
        "description": "Black undermines White's broad center with dynamic piece play and pressure on d4/c4."
    },
    # Intercontinental Ballistic Missile Gambit - Unsound but flashy gambit with heavy sacrifices.
    {
        "eco": "C40",
        "name": "Intercontinental Ballistic Missile Gambit",
        "moves": ["e4", "d5", "Nf3", "dxe4", "Ng5", "Nf6", "d3", "exd3", "Bxd3", "h6", "Nxf7", "Kxf7", "Bg6+", "Kxg6", "Qxd8"],
        "description": "An unsound yet spectacular gambit featuring early sacrifices and forcing play."
    }
]


# Precomputed list of opening lines as SAN arrays for fast prefix checks
OPENING_LINES_SAN: List[List[str]] = [
    opening["moves"]  # Now all moves are arrays
    for opening in OPENINGS
]


# Global book logic state
book_logic_active = True
candidate_openings = []
user_move_count = 0

def reset_book_logic():
    """Reset the book logic for a new game."""
    global book_logic_active, candidate_openings, user_move_count
    book_logic_active = True
    candidate_openings = []
    user_move_count = 0

def check_book_move_for_user(full_sequence: List[str], new_user_move: str) -> tuple[bool, Optional[Dict]]:
    """
    Check if a USER move is a book move using the candidate filtering approach.
    Only call this for USER moves, not Stockfish moves.
    
    Args:
        full_sequence: Current sequence of ALL moves (both sides) in SAN notation
        new_user_move: New USER move to check in SAN notation
        
    Returns:
        tuple: (is_book: bool, opening_info: Optional[Dict])
    """
    global book_logic_active, candidate_openings, user_move_count
    
    # If book logic is disabled, return false immediately
    if not book_logic_active:
        return (False, None)
    
    # Increment user move count
    user_move_count += 1
    
    # Stop checking after 5 user moves
    if user_move_count > 5:
        book_logic_active = False
        return (False, None)
    
    # Create the new sequence with the user's move
    new_sequence = full_sequence + [new_user_move]
    
    # First user move - initialize candidates
    if user_move_count == 1:
        candidate_openings = [
            opening for opening in OPENINGS 
            if len(opening["moves"]) > 0 and opening["moves"][0] == new_user_move
        ]
        
        if candidate_openings:
            return (True, candidate_openings[0])  # Return any matching opening info
        else:
            book_logic_active = False
            return (False, None)
    
    # Subsequent user moves - filter candidates
    candidate_openings = [
        opening for opening in candidate_openings
        if (len(opening["moves"]) >= len(new_sequence) and 
            opening["moves"][:len(new_sequence)] == new_sequence)
    ]
    
    if candidate_openings:
        return (True, candidate_openings[0])  # Return any matching opening info
    else:
        # No candidates match - permanently break book logic
        book_logic_active = False
        return (False, None)




