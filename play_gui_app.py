# FINAL FIXED VERSION
# play_gui_app.py

import streamlit as st
from stchess.component_board import board  # ✅ Use board directly as in your original working import
import chess
import chess.engine
import chess.pgn
import os

# === CONFIG ===
STOCKFISH_PATH = os.path.join("stockfish", "stockfish")  # Adjust path if needed

# === INIT ENGINE ===
if "engine" not in st.session_state:
    try:
        st.session_state.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    except Exception as e:
        st.error(f"Stockfish failed to start: {e}")
        st.stop()

# === INIT SESSION STATE ===
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
    st.session_state.moves = []
    st.session_state.game = chess.pgn.Game()

# === UI HEADER ===
st.title("♟ ChessMentor-AI")
st.markdown("Play as **White** against a 2000+ ELO Stockfish engine with a full React GUI board.")

# === RENDER REACT BOARD COMPONENT ===
user_move = board(
    color="white",
    key="chessboard"
)

# === HANDLE PLAYER MOVE ===
if user_move and "fen" in user_move and user_move["fen"] != st.session_state.board.fen():
    try:
        move_found = False
        for move in st.session_state.board.legal_moves:
            test_board = st.session_state.board.copy()
            test_board.push(move)
            if test_board.fen() == user_move["fen"]:
                st.session_state.board.push(move)
                st.session_state.moves.append(move.uci())
                move_found = True
                break

        if not move_found:
            st.warning("Couldn't find matching legal move for FEN.")

        # === AI MOVE ===
        if not st.session_state.board.is_game_over():
            result = st.session_state.engine.play(st.session_state.board, chess.engine.Limit(depth=15))
            ai_move = result.move
            st.session_state.board.push(ai_move)
            st.session_state.moves.append(ai_move.uci())

    except Exception as e:
        st.warning(f"Invalid move or error: {e}")

# === GAME END ===
if st.session_state.board.is_game_over():
    st.subheader("Game Over")
    st.text(f"Result: {st.session_state.board.result()}")

    # === BUILD PGN ===
    game = st.session_state.game
    node = game
    replay_board = chess.Board()
    for uci in st.session_state.moves:
        mv = replay_board.parse_uci(uci)
        node = node.add_variation(mv)
        replay_board.push(mv)

    os.makedirs("games", exist_ok=True)
    with open("games/last_game.pgn", "w") as f:
        print(game, file=f)

    st.download_button("Download PGN", data=str(game), file_name="game.pgn")

# === RESET ===
if st.button("Reset Game"):
    st.session_state.board = chess.Board()
    st.session_state.moves = []
    st.session_state.game = chess.pgn.Game()
    st.experimental_rerun()
