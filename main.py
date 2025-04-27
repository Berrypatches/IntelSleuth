"""
OSINT Microagent - Main Entry Point
This file provides access to both the FastAPI app
and the Flask redirector app
"""
# Import the FastAPI application
from fastapi_server import app as fastapi_app
# Import the Flask application
from flask_app import app as flask_app

# For Gunicorn WSGI
app = flask_app

# For FastAPI use
api_app = fastapi_app
if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", 8000))  # get the PORT from Render
    uvicorn.run("main:api_app", host="0.0.0.0", port=port, reload=False)
