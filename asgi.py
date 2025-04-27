"""
ASGI application for the OSINT Microagent.
This allows us to run a FastAPI application with Gunicorn.
"""
import importlib
import os
import sys

# Add the current directory to sys.path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the FastAPI application from main.py
from main import app

# Create an ASGI application that Gunicorn can work with through Uvicorn
application = app