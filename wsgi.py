"""
WSGI entry point for Gunicorn
This is a wrapper to allow Gunicorn to work with FastAPI through uvicorn.
"""
import os
import sys
import uvicorn

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Gunicorn will look for 'application' variable
from main import app
application = app