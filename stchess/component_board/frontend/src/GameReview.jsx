import React, { useState, useEffect } from "react";
import Chessboard from "chessboardjsx";
import "./ChessComponent.css";
const Chess = require("chess.js");

const GameReview = () => {
  const [currentMoveIndex, setCurrentMoveIndex] = useState(-1);
  const [gameData, setGameData] = useState(null);
  const [currentFen, setCurrentFen] = useState("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
  const [loading, setLoading] = useState(true);

  // Parse game data from URL parameters
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const gameParam = urlParams.get('game');
    
    if (gameParam) {
      try {
        const data = JSON.parse(decodeURIComponent(gameParam));
        setGameData(data);
        setCurrentMoveIndex(-1); // Start at initial position
        setLoading(false);
      } catch (error) {
        console.error('Failed to parse game data:', error);
        setLoading(false);
      }
    } else {
      setLoading(false);
    }
  }, []);

  // Handle arrow key navigation
  useEffect(() => {
    const handleKeyPress = (event) => {
      if (!gameData) return;
      
      if (event.key === 'ArrowRight') {
        // Next move
        if (currentMoveIndex < gameData.moves.length - 1) {
          setCurrentMoveIndex(currentMoveIndex + 1);
        }
      } else if (event.key === 'ArrowLeft') {
        // Previous move
        if (currentMoveIndex > -1) {
          setCurrentMoveIndex(currentMoveIndex - 1);
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [currentMoveIndex, gameData]);

  // Update board position based on current move index
  useEffect(() => {
    if (!gameData) return;
    
    if (currentMoveIndex === -1) {
      // Initial position
      setCurrentFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
    } else if (currentMoveIndex < gameData.moves.length) {
      // Show position after this move
      const moveData = gameData.moves[currentMoveIndex];
      setCurrentFen(moveData.fen);
    }
  }, [currentMoveIndex, gameData]);

  const goToMove = (index) => {
    if (index >= -1 && index < gameData.moves.length) {
      setCurrentMoveIndex(index);
    }
  };

  const getGameResultText = () => {
    if (!gameData) return "";
    return gameData.result === "1-0" ? "White wins!" : 
           gameData.result === "0-1" ? "Black wins!" : "Draw!";
  };

  if (loading) {
    return (
      <div style={{ 
        padding: "20px", 
        color: "white", 
        textAlign: "center",
        backgroundColor: "#1a1a1a",
        minHeight: "100vh"
      }}>
        Loading game review...
      </div>
    );
  }

  if (!gameData) {
    return (
      <div style={{ 
        padding: "20px", 
        color: "white", 
        textAlign: "center",
        backgroundColor: "#1a1a1a",
        minHeight: "100vh"
      }}>
        No game data found. Please start a game first.
      </div>
    );
  }

  return (
    <div style={{ 
      padding: "20px", 
      backgroundColor: "#1a1a1a", 
      minHeight: "100vh", 
      color: "white" 
    }}>
      <h2 style={{ textAlign: "center", marginBottom: "20px" }}>
        Game Review - {getGameResultText()}
      </h2>
      
      <div style={{ textAlign: "center", marginBottom: "20px", fontSize: "16px" }}>
        <strong>Use ← → arrow keys to navigate through moves</strong>
      </div>
      
      <div style={{ display: "flex", gap: "20px", justifyContent: "center" }}>
        {/* Chess Board */}
        <div style={{ flex: "0 0 auto" }}>
          <Chessboard
            width={400}
            position={currentFen}
            showNotation={true}
            orientation="white"
            boardStyle={{
              borderRadius: "5px",
              boxShadow: `0 5px 15px rgba(0, 0, 0, 0.5)`,
            }}
          />
        </div>
        
        {/* Move List */}
        <div style={{ flex: "0 0 300px", padding: "20px" }}>
          <h3>Move History</h3>
          <div style={{ maxHeight: "400px", overflowY: "auto" }}>
            {currentMoveIndex === -1 && (
              <div style={{
                padding: "8px",
                margin: "4px 0",
                backgroundColor: "#4CAF50",
                borderRadius: "4px",
                fontWeight: "bold"
              }}>
                Initial Position
              </div>
            )}
            {gameData.moves.map((moveData, index) => (
              <div 
                key={index}
                onClick={() => goToMove(index)}
                style={{
                  padding: "8px",
                  margin: "4px 0",
                  backgroundColor: index === currentMoveIndex ? "#4CAF50" : "rgba(255, 255, 255, 0.1)",
                  borderRadius: "4px",
                  cursor: "pointer",
                  fontWeight: index === currentMoveIndex ? "bold" : "normal"
                }}
              >
                {index + 1}. {moveData.move}
              </div>
            ))}
          </div>
          
          {/* Navigation Controls */}
          <div style={{ marginTop: "20px", textAlign: "center" }}>
            <button 
              onClick={() => goToMove(-1)}
              style={{ 
                margin: "0 5px", 
                padding: "8px 16px",
                backgroundColor: "#2196F3",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer"
              }}
            >
              Start
            </button>
            <button 
              onClick={() => goToMove(currentMoveIndex - 1)}
              disabled={currentMoveIndex <= -1}
              style={{ 
                margin: "0 5px", 
                padding: "8px 16px",
                backgroundColor: currentMoveIndex <= -1 ? "#666" : "#2196F3",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: currentMoveIndex <= -1 ? "not-allowed" : "pointer"
              }}
            >
              Previous
            </button>
            <button 
              onClick={() => goToMove(currentMoveIndex + 1)}
              disabled={currentMoveIndex >= gameData.moves.length - 1}
              style={{ 
                margin: "0 5px", 
                padding: "8px 16px",
                backgroundColor: currentMoveIndex >= gameData.moves.length - 1 ? "#666" : "#2196F3",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: currentMoveIndex >= gameData.moves.length - 1 ? "not-allowed" : "pointer"
              }}
            >
              Next
            </button>
            <button 
              onClick={() => goToMove(gameData.moves.length - 1)}
              style={{ 
                margin: "0 5px", 
                padding: "8px 16px",
                backgroundColor: "#2196F3",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer"
              }}
            >
              End
            </button>
          </div>
          
          <div style={{ marginTop: "10px", textAlign: "center", fontSize: "14px" }}>
            {currentMoveIndex === -1 ? "Initial Position" : `Move ${currentMoveIndex + 1} of ${gameData.moves.length}`}
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameReview; 