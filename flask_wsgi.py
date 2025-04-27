"""
WSGI entry point for Gunicorn with Flask
"""
import os
import sys

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask application
from flask_app import app

# Application entry point for Gunicorn
application = app