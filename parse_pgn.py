import chess.pgn

def extract_positions(pgn_path):
    positions = []

    with open(pgn_path, 'r') as pgn_file:
        game = chess.pgn.read_game(pgn_file)
        board = game.board()

        for move in game.mainline_moves():
            board.push(move)
            positions.append(board.fen())

    return positions

# Optional test code, only runs if this file is executed directly
if __name__ == "__main__":
    path = "games/sample.pgn"
    fens = extract_positions(path)
    for i, fen in enumerate(fens, 1):
        print(f"{i}: {fen}")
