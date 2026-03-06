"""
Vercel Serverless Entrypoint
AI Medical Report Analyzer

This file is the single entrypoint for Vercel's Python runtime.
It imports and re-exports the FastAPI `app` object from the main module.
"""

import os
import sys

# Add the project root to the sys.path so 'app' can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app

