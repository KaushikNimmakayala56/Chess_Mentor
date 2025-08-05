from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chess
import chess.engine
import os
from starlette.responses import JSONResponse
from move_classification import classify_move, generate_feedback_message

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
    
    # Apply best move to get its evaluation for CPL calculation
    board_after_best = board_before.copy()
    board_after_best.push(best_move)
    analysis_after_best = engine.analyse(board_after_best, chess.engine.Limit(depth=5))
    score_after_best_move = analysis_after_best["score"].relative.score(mate_score=10000)
    
    # Calculate CPL (Centipawn Loss) - user move vs best move
    score_after_user_move = score_after
    cpl = abs(score_after_best_move - score_after_user_move)
    
    return {
        'material_change': material_change,
        'positional_change': positional_change,
        'best_move': best_move_san,
        'move_san': board_before.san(move),
        'cpl': cpl
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
        
        # Store FEN before the move
        fen_before_move = board.fen()
        
        # Apply user's move
        board.push(move)
        
        # Add user move to history with FEN (before the move)
        move_data = {
            'move': analysis_result['move_san'],
            'fen': fen_before_move  # FEN before the move
        }
        move_history.append(move_data)
        
        # Generate feedback for USER'S move only using CPL
        classification = classify_move(analysis_result['cpl'])
        feedback = generate_feedback_message(classification,
                                           analysis_result['cpl'],
                                           analysis_result['move_san'],
                                           analysis_result['best_move'])
        
        # Stockfish move - NO ANALYSIS, just apply the move
        ai_move = None
        if not board.is_game_over():
            result = engine.play(board, chess.engine.Limit(depth=5))
            ai_move = result.move
            # Store FEN before AI move
            fen_before_ai_move = board.fen()
            # Add Stockfish move to history with FEN (before the move)
            ai_move_data = {
                'move': board.san(ai_move),
                'fen': fen_before_ai_move  # FEN before the move
            }
            move_history.append(ai_move_data)
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
                'user_move': analysis_result['move_san'],
                'cpl': analysis_result['cpl']
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

def main():
    """Main entry point for the chess application"""
    import uvicorn
    import webbrowser
    import threading
    import time
    import os
    
    # Start the FastAPI server
    def start_server():
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    
    # Start React frontend
    def start_frontend():
        import subprocess
        frontend_path = os.path.join(os.path.dirname(__file__), "..", "stchess", "component_board", "frontend")
        if os.path.exists(frontend_path):
            subprocess.Popen(["npm", "start"], cwd=frontend_path)
    
    print("🚀 Starting ChessMentor-AI...")
    print("📡 Backend API: http://localhost:8000")
    print("🎮 Frontend GUI: http://localhost:3000")
    
    # Start backend in a separate thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait a moment for server to start
    time.sleep(2)
    
    # Start frontend
    try:
        start_frontend()
        time.sleep(3)
        # Open browser to the React app
        webbrowser.open("http://localhost:3000")
    except Exception as e:
        print(f"⚠️  Could not start frontend automatically: {e}")
        print("🔧 Please run manually: cd stchess/component_board/frontend && npm start")
    
    print("✅ ChessMentor-AI is running!")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down ChessMentor-AI...")

if __name__ == "__main__":
    main() 