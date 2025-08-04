import React, { useState, useEffect, useRef } from "react";
import Chessboard from "chessboardjsx";
import "./ChessComponent.css";
const Chess = require("chess.js");

const API_BASE = "http://127.0.0.1:8000";

const ChessComponent = ({ color }) => {
  let startFen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
  const chess = useRef(new Chess(startFen));
  const [fen, setFen] = useState(startFen);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [gameOver, setGameOver] = useState(false);
  const [gameResult, setGameResult] = useState("");
  const [moveHistory, setMoveHistory] = useState([]);
  const [feedback, setFeedback] = useState("");

  // Helper: get turn from FEN
  const getTurn = (fenStr) => {
    if (!fenStr) return null;
    return fenStr.split(" ")[1] === "w" ? "white" : "black";
  };
  const isWhiteTurn = getTurn(fen) === "white";

  // Helper: get king square and check status
  const getCheckInfo = () => {
    if (!fen) return { inCheck: false, kingSquare: null };
    const tempChess = new Chess(fen);
    const inCheck = tempChess.in_check();
    let kingSquare = null;
    if (inCheck) {
      // Find the king's square
      for (let square of tempChess.SQUARES) {
        const piece = tempChess.get(square);
        if (piece && piece.type === 'k' && piece.color === (isWhiteTurn ? 'w' : 'b')) {
          kingSquare = square;
          break;
        }
      }
    }
    return { inCheck, kingSquare };
  };

  const { inCheck, kingSquare } = getCheckInfo();

  // Custom square styles for check highlighting
  const squareStyles = inCheck && kingSquare ? {
    [kingSquare]: { backgroundColor: 'rgba(255, 0, 0, 0.4)' }
  } : {};

  // Fetch initial board state
  useEffect(() => {
    fetch(`${API_BASE}/state`)
      .then(res => res.json())
      .then(data => {
        setFen(data.fen);
        chess.current.load(data.fen);
        setGameOver(data.is_game_over || false);
        setGameResult(data.result || "");
      });
    
    // Fetch move history
    fetch(`${API_BASE}/history`)
      .then(res => res.json())
      .then(data => {
        setMoveHistory(data.moves || []);
      });
  }, []);

  // Helper: format move history for display
  const formatMoveHistory = (moves) => {
    const formatted = [];
    for (let i = 0; i < moves.length; i += 2) {
      const moveNumber = Math.floor(i / 2) + 1;
      const whiteMove = moves[i];
      const blackMove = moves[i + 1];
      formatted.push(`${moveNumber}. ${whiteMove}${blackMove ? ` ${blackMove}` : ''}`);
    }
    return formatted;
  };

  // Handle user move
  const handleMove = (move) => {
    if (gameOver) {
      setError("Game is over. Click Reset to start a new game.");
      return false; // Prevent visual move
    }
    if (!isWhiteTurn) {
      setError("It's not your turn. Wait for Stockfish to move.");
      return false; // Prevent visual move
    }
    
    // Always ensure chess.js is loaded with current backend FEN
    chess.current.load(fen);
    
    let moveToSend = { from: move.from, to: move.to };
    const isWhitePawn = chess.current.get(move.from)?.type === 'p' && chess.current.get(move.from)?.color === 'w';
    if (isWhitePawn && move.to[1] === '8') {
      let promo = prompt("Promote pawn to (q=Queen, n=Knight, r=Rook, b=Bishop):", "q");
      if (!['q', 'n', 'r', 'b'].includes(promo)) promo = 'q';
      moveToSend.promotion = promo;
    }
    
    // Check if move is legal locally first
    if (!chess.current.move(moveToSend)) {
      setError("Illegal move. Try again.");
      setTimeout(() => setError(""), 3000);
      return false; // Prevent visual move
    }
    
    // If legal locally, send to backend
    setLoading(true);
    fetch(`${API_BASE}/move`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ move: moveToSend })
    })
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          setError(data.error);
          // Reset board to current backend state on error
          fetch(`${API_BASE}/state`)
            .then(res => res.json())
            .then(stateData => {
              setFen(stateData.fen);
              chess.current.load(stateData.fen);
              setGameOver(stateData.is_game_over || false);
              setGameResult(stateData.result || "");
            });
          // Clear error after 3 seconds
          setTimeout(() => setError(""), 3000);
        } else {
          setFen(data.fen);
          chess.current.load(data.fen);
          setGameOver(data.is_game_over || false);
          setGameResult(data.result || "");
          setMoveHistory(data.move_history || []);
          setFeedback(data.analysis?.feedback || "");
          setError("");
        }
        setLoading(false);
      })
      .catch(() => {
        setError("Network error");
        setLoading(false);
        // Clear error after 3 seconds
        setTimeout(() => setError(""), 3000);
      });
    
    return true; // Allow visual move only if legal
  };

  // Handle reset
  const handleReset = () => {
    setLoading(true);
    fetch(`${API_BASE}/reset`, { method: "POST" })
      .then(res => res.json())
      .then(data => {
        setFen(data.fen);
        chess.current.load(data.fen);
        setError("");
        setGameOver(false);
        setGameResult("");
        setMoveHistory([]);
        setFeedback("");
        setLoading(false);
      });
  };

  // Helper: get feedback styling
  const getFeedbackStyle = (feedback) => {
    if (feedback.includes("Excellent") || feedback.includes("Good")) {
      return { background: "#4CAF50", color: "white" };
    } else if (feedback.includes("Okay")) {
      return { background: "#FF9800", color: "white" };
    } else if (feedback.includes("Inaccuracy") || feedback.includes("Blunder")) {
      return { background: "#F44336", color: "white" };
    } else {
      return { background: "#2196F3", color: "white" };
    }
  };

  return (
    <div className="flex-center">
      <h4>Kaushik Chess APP</h4>
      <div style={{ display: "flex", gap: "20px", alignItems: "flex-start" }}>
        <div style={{ position: "relative" }}>
          <Chessboard
            width={400}
            id="chessboard"
            position={fen}
            transitionDuration={300}
            showNotation={true}
            orientation={color}
            squareStyles={squareStyles}
            boardStyle={{
              borderRadius: "5px",
              boxShadow: `0 5px 15px rgba(0, 0, 0, 0.5)`,
              marginBottom: "20px",
            }}
            onDrop={isWhiteTurn && !loading && !gameOver ? (move) => handleMove({ from: move.sourceSquare, to: move.targetSquare }) : undefined}
            draggable={isWhiteTurn && !loading && !gameOver}
          />
        </div>
        
        {/* Move History - Right Side */}
        {moveHistory.length > 0 && (
          <div style={{ 
            padding: 15, 
            backgroundColor: "rgba(255, 255, 255, 0.1)", 
            borderRadius: 8,
            width: 200,
            maxHeight: 400,
            overflowY: "auto"
          }}>
            <h5 style={{ margin: "0 0 10px 0", color: "#fff" }}>Move History:</h5>
            <div style={{ fontSize: "14px" }}>
              {formatMoveHistory(moveHistory).map((move, index) => (
                <div key={index} style={{ color: "#fff", padding: "2px 0" }}>
                  {move}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      
      {/* Move Feedback */}
      {feedback && (
        <div style={{
          padding: "10px 20px",
          borderRadius: "8px",
          margin: "10px 0",
          textAlign: "center",
          fontWeight: "bold",
          ...getFeedbackStyle(feedback)
        }}>
          {feedback}
        </div>
      )}
      
      <p style={{ color: "#fff", margin: 0 }}>Turn: {isWhiteTurn ? "White (You)" : "Black (AI)"}</p>
      {error && <div style={{ background: "#bfa", color: "#222", padding: 8, borderRadius: 6, margin: 8 }}>{error}</div>}
      
      {/* Game Result at Bottom */}
      {gameOver && (
        <div style={{
          padding: "15px 20px",
          borderRadius: "8px",
          margin: "10px 0",
          textAlign: "center",
          fontWeight: "bold",
          backgroundColor: gameResult === "1-0" ? "#4CAF50" : gameResult === "0-1" ? "#F44336" : "#FF9800",
          color: "white"
        }}>
          {gameResult === "1-0" ? "White wins!" : gameResult === "0-1" ? "Black wins!" : "Draw!"}
        </div>
      )}
      
      <button onClick={handleReset} disabled={loading} style={{ marginTop: 16 }}>Reset Game</button>
    </div>
  );
};

export default ChessComponent;


