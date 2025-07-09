from flask import Flask, request, jsonify
import chess
import chess.pgn
import chess.engine
import io

app = Flask(__name__)

# Point to the Stockfish binary we just un-quarantined
STOCKFISH_PATH = "./stockfish/stockfish"

@app.route('/analyze', methods=['POST'])
def analyze_game():
    try:
        pgn_text = request.form['pgn']
        game = chess.pgn.read_game(io.StringIO(pgn_text))
        board = game.board()
        analysis = []

        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
            for move in game.mainline_moves():
                board.push(move)
                info = engine.analyse(board, chess.engine.Limit(depth=12))
                best_move = engine.play(board, chess.engine.Limit(time=0.1)).move
                analysis.append({
                    "move": board.san(move),
                    "score": info["score"].relative.score(mate_score=10000),
                    "best_move": board.san(best_move)
                })

        return jsonify({"analysis": analysis})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
