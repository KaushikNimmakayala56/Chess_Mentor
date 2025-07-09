import chess.engine
import json
from parse_pgn import extract_positions

# Path to Stockfish engine
engine_path = "/opt/homebrew/bin/stockfish"

# Load FEN positions from PGN
fens = extract_positions("games/sample.pgn")

# Start Stockfish engine
engine = chess.engine.SimpleEngine.popen_uci(engine_path)

evaluations = []

print(f"PGN parsed — total positions: {len(fens)}")

for i, fen in enumerate(fens):
    board = chess.Board(fen)
    info = engine.analyse(board, chess.engine.Limit(depth=12))
    score = info["score"].white()

    print(f"{i+1}: Score = {score.score()}")  # Debug print

    # Save to list
    evaluations.append({
        "fen": fen,
        "score": score.__dict__,
        "white_to_move": board.turn
    })

engine.quit()

# Save to JSON
with open("evals.json", "w") as f:
    json.dump(evaluations, f, indent=2)

print("Saved evaluations to evals.json")
