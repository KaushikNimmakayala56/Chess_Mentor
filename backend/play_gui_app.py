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
st.title("KaushikChessAPP")
st.markdown("Play as **White** against a 2000+ ELO Stockfish engine with a full React GUI board.")

# === RENDER REACT BOARD COMPONENT ===
user_move = board(
    color="white",
    fen=st.session_state.board.fen(),
    key="chessboard"
)

# === HANDLE PLAYER MOVE ===
if user_move and "move" in user_move:
    # Debug: Print FEN received from frontend and backend's current FEN
    print("[DEBUG] FEN from frontend:", user_move.get("fen"))
    print("[DEBUG] Backend board FEN before move:", st.session_state.board.fen())
    move_dict = user_move["move"]
    move_uci = move_dict["from"] + move_dict["to"]
    if "promotion" in move_dict and move_dict["promotion"]:
        move_uci += move_dict["promotion"]
    print("[DEBUG] Attempting to apply move:", move_uci)
    move = chess.Move.from_uci(move_uci)
    try:
        st.session_state.board.push(move)
        st.session_state.moves.append(move.uci())
        print("[DEBUG] Backend board FEN after user move:", st.session_state.board.fen())
        # Stockfish move
        ai_move = None
        if not st.session_state.board.is_game_over():
            result = st.session_state.engine.play(st.session_state.board, chess.engine.Limit(depth=15))
            ai_move = result.move
            print("[DEBUG] Stockfish move:", ai_move)
            st.session_state.board.push(ai_move)
            st.session_state.moves.append(ai_move.uci())
            print("[DEBUG] Backend board FEN after Stockfish move:", st.session_state.board.fen())
        # Instead of st.json and st.stop, just let the rerun happen and pass the latest FEN as a prop
    except Exception as e:
        print("[DEBUG] Exception while applying move:", e)
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
    st.rerun()
