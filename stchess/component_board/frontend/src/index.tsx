import React from "react"
import ReactDOM from "react-dom"
import ChessComponent from "./ChessComponent"

ReactDOM.render(
  <React.StrictMode>
    <ChessComponent color="white" />
  </React.StrictMode>,
  document.getElementById("root")
)
