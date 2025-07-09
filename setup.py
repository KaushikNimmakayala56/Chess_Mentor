"""
Setup script for ChessMentor-AI
"""
from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="chessmentor-ai",
    version="0.1.0",
    author="ChessMentor-AI Team",
    author_email="kaushiksubs03@gmail.com",
    description="A browser-based chess mentor application with Stockfish AI",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/KaushikNimmakayala56/Chess_Mentor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=5.0.0",
            "black>=24.1.1",
            "flake8>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "chessmentor=play_gui_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
    keywords="chess, ai, stockfish, streamlit, education, game",
    project_urls={
        "Bug Reports": "https://github.com/KaushikNimmakayala56/Chess_Mentor/issues",
        "Source": "https://github.com/KaushikNimmakayala56/Chess_Mentor",
        "Documentation": "https://github.com/KaushikNimmakayala56/Chess_Mentor#readme",
    },
) 