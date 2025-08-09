from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chess
import chess.engine
import os
from starlette.responses import JSONResponse
from move_classification import classify_move, generate_feedback_message
from openings import check_book_move_for_user, reset_book_logic

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
full_san_sequence = []  # Track both sides' SAN moves for book streak

# Simple game storage for review (max 10 games)
from collections import OrderedDict
stored_games = OrderedDict()
MAX_STORED_GAMES = 10

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

def analyze_move_quality(board_before, move, engine, full_sequence):
    """Analyze the quality of a move considering material and position"""
    # Get material count before move
    material_before = get_material_count(board_before)
    
    # Apply the move
    board_after = board_before.copy()
    board_after.push(move)
    move_san = board_before.san(move)
    
    # Check if this USER move is a book move
    is_book, opening_info = check_book_move_for_user(full_sequence, move_san)
    
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
        'move_san': move_san,
        'cpl': cpl,
        'is_book': is_book,
        'opening_info': opening_info
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
    global move_history, full_san_sequence
    move_dict = req.move
    move_uci = move_dict['from'] + move_dict['to']
    if 'promotion' in move_dict and move_dict['promotion']:
        move_uci += move_dict['promotion']
    move = chess.Move.from_uci(move_uci)
    try:
        # Analyze the user's move quality with current sequence
        analysis_result = analyze_move_quality(board, move, engine, full_san_sequence)
        
        # Store FEN before the move
        fen_before_move = board.fen()
        
        # Apply user's move
        board.push(move)
        
        # Update full SAN sequence with user's move
        full_san_sequence.append(analysis_result['move_san'])
        
        # Add user move to history with FEN (before the move)
        move_data = {
            'move': analysis_result['move_san'],
            'fen': fen_before_move  # FEN before the move
        }
        move_history.append(move_data)
        
        # Generate feedback for USER'S move only using CPL and book detection
        classification = classify_move(analysis_result['cpl'], analysis_result['is_book'])
        
        # Use opening info from analysis (already computed in analyze_move_quality)
        opening_info = analysis_result['opening_info']
        
        feedback = generate_feedback_message(classification,
                                           analysis_result['cpl'],
                                           analysis_result['move_san'],
                                           analysis_result['best_move'],
                                           opening_info)
        
        # Stockfish move - NO ANALYSIS, just apply the move
        ai_move = None
        if not board.is_game_over():
            result = engine.play(board, chess.engine.Limit(depth=5))
            ai_move = result.move
            # Store FEN before AI move
            fen_before_ai_move = board.fen()
            # Add Stockfish move to history with FEN (before the move)
            ai_move_san = board.san(ai_move)
            ai_move_data = {
                'move': ai_move_san,
                'fen': fen_before_ai_move  # FEN before the move
            }
            move_history.append(ai_move_data)
            board.push(ai_move)

            # Update full SAN sequence with AI move - this may break the book streak
            full_san_sequence.append(ai_move_san)
        
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
    global board, move_history, full_san_sequence
    board = chess.Board()
    move_history = []
    full_san_sequence = []
    reset_book_logic()  # Reset the book logic state
    return {'fen': board.fen()}

@app.post("/store-game")
def store_game(request: Request):
    import uuid
    import asyncio
    
    async def get_body():
        return await request.json()
    
    game_data = asyncio.run(get_body())
    game_id = str(uuid.uuid4())
    
    # Add timestamp for display
    import datetime
    game_data['timestamp'] = datetime.datetime.now().isoformat()
    
    # Remove oldest game if we're at the limit
    if len(stored_games) >= MAX_STORED_GAMES:
        stored_games.popitem(last=False)  # Remove oldest (first item)
    
    stored_games[game_id] = game_data
    return {"game_id": game_id}

@app.get("/game/{game_id}")
def get_game(game_id: str):
    if game_id in stored_games:
        return stored_games[game_id]
    return {"error": "Game not found"}

@app.get("/games")
def list_games():
    """List all stored games with basic info"""
    games_list = []
    for game_id, game_data in stored_games.items():
        games_list.append({
            "id": game_id,
            "result": game_data.get("result", "Unknown"),
            "timestamp": game_data.get("timestamp", "Unknown"),
            "move_count": len(game_data.get("moves", [])),
            "url": f"/review?id={game_id}"
        })
    return {"games": games_list, "total": len(games_list), "max_limit": MAX_STORED_GAMES}

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