import React from "react"
import ReactDOM from "react-dom"
import ChessComponent from "./ChessComponent"
import GameReview from "./GameReview"

// Simple routing
const App = () => {
  const path = window.location.pathname;
  
  if (path.includes('/review')) {
    return <GameReview />;
  }
  
  return <ChessComponent color="white" />;
};

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById("root")
)
