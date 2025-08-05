from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chess
import chess.engine
import os
from starlette.responses import JSONResponse

app = FastAPI()

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STOCKFISH_PATH = os.path.join("..", "stockfish", "stockfish")

# Global state (for MVP, not for production)
board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
move_history = []  # Track moves for history

class MoveRequest(BaseModel):
    move: dict

class FenRequest(BaseModel):
    fen: str

@app.get("/state")
def get_state():
    return {
        'fen': board.fen(),
        'is_game_over': board.is_game_over(),
        'result': board.result() if board.is_game_over() else None
    }

@app.get("/history")
def get_history():
    return {
        'moves': move_history,
        'total_moves': len(move_history)
    }

@app.get("/analyze")
def analyze_position():
    """Analyze current position and return evaluation"""
    try:
        info = engine.analyse(board, chess.engine.Limit(depth=5))
        score = info["score"].relative.score(mate_score=10000)
        
        # Get best move
        best_move = engine.play(board, chess.engine.Limit(depth=5)).move
        best_move_san = board.san(best_move)
        
        return {
            'evaluation': score,
            'best_move': best_move_san,
            'fen': board.fen()
        }
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.put("/state")
def set_state(req: FenRequest):
    global board, move_history
    try:
        board = chess.Board(req.fen)
        # Rebuild move history from the new FEN
        move_history = []
        temp_board = chess.Board()
        for move in board.move_stack:
            move_history.append(temp_board.san(move))
            temp_board.push(move)
        return {"fen": board.fen()}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

def analyze_move_quality(board_before, move, engine):
    """Analyze the quality of a move considering material and position"""
    # Get material count before move
    material_before = get_material_count(board_before)
    
    # Apply the move
    board_after = board_before.copy()
    board_after.push(move)
    
    # Get material count after move
    material_after = get_material_count(board_after)
    
    # Calculate material change (positive = gain, negative = loss)
    material_change = material_after - material_before
    
    # Get engine evaluation before and after
    analysis_before = engine.analyse(board_before, chess.engine.Limit(depth=5))
    score_before = analysis_before["score"].relative.score(mate_score=10000)
    
    analysis_after = engine.analyse(board_after, chess.engine.Limit(depth=5))
    score_after = analysis_after["score"].relative.score(mate_score=10000)
    
    # Calculate positional change (from White's perspective)
    positional_change = score_after - score_before
    
    # Get best move for comparison
    best_move = engine.play(board_before, chess.engine.Limit(depth=5)).move
    best_move_san = board_before.san(best_move)
    
    return {
        'material_change': material_change,
        'positional_change': positional_change,
        'best_move': best_move_san,
        'move_san': board_before.san(move)
    }

def get_material_count(board):
    """Calculate material count for White (positive) vs Black (negative)"""
    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }
    
    white_material = 0
    black_material = 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                white_material += value
            else:
                black_material += value
    
    return white_material - black_material

def get_move_feedback(analysis_result):
    """Generate feedback based on material and positional analysis"""
    material_change = analysis_result['material_change']
    positional_change = analysis_result['positional_change']
    best_move = analysis_result['best_move']
    user_move = analysis_result['move_san']
    
    # Material loss is always bad
    if material_change < -50:
        if material_change < -200:
            return f"Your move {user_move}: Blunder! You lost material (-{abs(material_change)/100:.1f}) (Best: {best_move})"
        else:
            return f"Your move {user_move}: Inaccuracy. You lost material (-{abs(material_change)/100:.1f}) (Best: {best_move})"
    
    # Material gain is always good
    elif material_change > 50:
        if material_change > 200:
            return f"Your move {user_move}: Excellent! You won material (+{material_change/100:.1f})"
        else:
            return f"Your move {user_move}: Good move! You won material (+{material_change/100:.1f})"
    
    # No material change, evaluate by position
    else:
        if positional_change > 200:
            return f"Your move {user_move}: Excellent! +{positional_change/100:.1f}"
        elif positional_change > 50:
            return f"Your move {user_move}: Good move! +{positional_change/100:.1f}"
        elif positional_change > -50:
            return f"Your move {user_move}: Okay move. {positional_change/100:.1f}"
        elif positional_change > -200:
            return f"Your move {user_move}: Inaccuracy. {positional_change/100:.1f} (Best: {best_move})"
        else:
            return f"Your move {user_move}: Blunder! {positional_change/100:.1f} (Best: {best_move})"

@app.post("/move")
def make_move(req: MoveRequest):
    global move_history
    move_dict = req.move
    move_uci = move_dict['from'] + move_dict['to']
    if 'promotion' in move_dict and move_dict['promotion']:
        move_uci += move_dict['promotion']
    move = chess.Move.from_uci(move_uci)
    try:
        # Analyze the user's move quality
        analysis_result = analyze_move_quality(board, move, engine)
        
        # Apply user's move
        board.push(move)
        
        # Add user move to history
        move_history.append(analysis_result['move_san'])
        
        # Generate feedback for USER'S move only
        feedback = get_move_feedback(analysis_result)
        
        # Stockfish move - NO ANALYSIS, just apply the move
        ai_move = None
        if not board.is_game_over():
            result = engine.play(board, chess.engine.Limit(depth=5))
            ai_move = result.move
            # Add Stockfish move to history (no analysis)
            move_history.append(board.san(ai_move))
            board.push(ai_move)
        
        return {
            'fen': board.fen(),
            'ai_move': ai_move.uci() if ai_move else None,
            'is_game_over': board.is_game_over(),
            'result': board.result() if board.is_game_over() else None,
            'move_history': move_history,
            'analysis': {
                'material_change': analysis_result['material_change'],
                'positional_change': analysis_result['positional_change'],
                'feedback': feedback,
                'best_move': analysis_result['best_move'],
                'user_move': analysis_result['move_san']
            }
        }
    except Exception as e:
        return JSONResponse(status_code=400, content={'error': str(e), 'fen': board.fen()})

@app.post("/reset")
def reset():
    global board, move_history
    board = chess.Board()
    move_history = []
    return {'fen': board.fen()}

@app.on_event("shutdown")
def shutdown_event():
    engine.quit() 