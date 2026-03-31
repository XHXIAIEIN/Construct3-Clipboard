"""Construct3-Clipboard Service Configuration"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).parent.parent

# Service
HOST = os.getenv("CLIPBOARD_HOST", "0.0.0.0")
PORT = int(os.getenv("CLIPBOARD_PORT", "8766"))

# RAG dependency (for ACE validation)
RAG_API_URL = os.getenv("RAG_API_URL", "http://localhost:8765")

# Error notebook
ERRORS_DIR = BASE_DIR / "errors"
