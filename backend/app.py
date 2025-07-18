from flask import Flask, request, jsonify, session
import chess
import chess.pgn
import chess.engine
import io
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = 'supersecretkey'  # Needed for session

# Point to the Stockfish binary we just un-quarantined
STOCKFISH_PATH = os.path.join("stockfish", "stockfish")

# Helper to get or create board and engine in session
def get_board():
    if 'fen' not in session:
        session['fen'] = chess.STARTING_FEN
    return chess.Board(session['fen'])

def set_board(board):
    session['fen'] = board.fen()

def get_engine():
    if not hasattr(app, 'engine'):
        app.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    return app.engine

@app.route('/state', methods=['GET'])
def get_state():
    board = get_board()
    return jsonify({
        'fen': board.fen(),
        'is_game_over': board.is_game_over(),
        'result': board.result() if board.is_game_over() else None
    })

@app.route('/move', methods=['POST'])
def make_move():
    data = request.json
    move_dict = data.get('move')
    board = get_board()
    move_uci = move_dict['from'] + move_dict['to']
    if 'promotion' in move_dict and move_dict['promotion']:
        move_uci += move_dict['promotion']
    move = chess.Move.from_uci(move_uci)
    try:
        board.push(move)
        # Stockfish move
        ai_move = None
        if not board.is_game_over():
            engine = get_engine()
            result = engine.play(board, chess.engine.Limit(depth=15))
            ai_move = result.move
            board.push(ai_move)
        set_board(board)
        return jsonify({
            'fen': board.fen(),
            'ai_move': ai_move.uci() if ai_move else None,
            'is_game_over': board.is_game_over(),
            'result': board.result() if board.is_game_over() else None
        })
    except Exception as e:
        return jsonify({'error': str(e), 'fen': board.fen()}), 400

@app.route('/reset', methods=['POST'])
def reset():
    session['fen'] = chess.STARTING_FEN
    return jsonify({'fen': session['fen']})


if __name__ == '__main__':
    app.run(debug=True)
