# play_chess_streamlit.py

import streamlit as st
import chess
import chess.engine

# Setup
stockfish_path = "/opt/homebrew/bin/stockfish"
engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)

# Streamlit session state
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "game_over" not in st.session_state:
    st.session_state.game_over = False

st.title("♟️ ChessMentor-AI")
st.markdown("Play as White against 2000+ ELO Stockfish.")

# Display board
st.text(str(st.session_state.board))

# Only show input if game isn't over
if not st.session_state.game_over and not st.session_state.board.is_game_over():
    move_input = st.text_input("Enter your move (UCI format like e2e4):")

    if st.button("Make Move"):
        try:
            user_move = chess.Move.from_uci(move_input)
            if user_move in st.session_state.board.legal_moves:
                st.session_state.board.push(user_move)

                # Stockfish move
                result = engine.play(st.session_state.board, chess.engine.Limit(depth=15))
                st.session_state.board.push(result.move)
            else:
                st.warning("Illegal move. Try again.")
        except:
            st.error("Invalid input format. Use UCI like e2e4.")

# If game is over
if st.session_state.board.is_game_over():
    st.session_state.game_over = True
    st.success("Game over! Result: " + st.session_state.board.result())

if st.button("Reset Game"):
    st.session_state.board = chess.Board()
    st.session_state.game_over = False
    st.rerun()

engine.quit()
