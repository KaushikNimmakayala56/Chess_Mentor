import os
import streamlit.components.v1 as components

# Path to frontend build
_parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(_parent_dir, "frontend", "build")

# Declare Streamlit component
chessboard_component = components.declare_component(
    "chessboard_component",
    path=build_dir
)