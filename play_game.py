# play_game.py

import chess
import chess.engine
import chess.pgn
import os

# Path to Stockfish
engine_path = "/opt/homebrew/bin/stockfish"
engine = chess.engine.SimpleEngine.popen_uci(engine_path)

# Create a new game and board
game = chess.pgn.Game()
board = game.board()

print("Welcome to ChessMentor-AI 🎯")
print("You're playing as White. Enter moves in UCI format (e.g., e2e4).")

while not board.is_game_over():
    # Show current board
    print("\n" + str(board))

    # Get player's move
    move_uci = input("Your move: ").strip()

    try:
        move = chess.Move.from_uci(move_uci)
        if move not in board.legal_moves:
            raise ValueError
        board.push(move)
    except:
        print("Invalid move. Try again.")
        continue

    # Stockfish responds
    if not board.is_game_over():
        result = engine.play(board, chess.engine.Limit(depth=12))
        board.push(result.move)
        print(f"Stockfish played: {result.move}")

# Game ended
print("\nGame over!")
print("Result:", board.result())

# Save PGN
pgn_path = "games/played_game.pgn"
with open(pgn_path, "w") as f:
    exporter = chess.pgn.FileExporter(f)
    game.add_line(board.move_stack)
    game.headers["Result"] = board.result()
    game.accept(exporter)

print(f"Saved PGN to {pgn_path}")

# Quit engine
engine.quit()

# Run Post-Game Analysis
print("\nRunning post-game evaluation...")
os.system("python3 evaluate_fens.py")
os.system("python3 generate_prompts.py")
os.system("python3 coach_moves.py")
