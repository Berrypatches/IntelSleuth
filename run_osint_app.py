"""
OSINT Microagent - FastAPI Server Runner
This script starts the FastAPI server on port 8000.
"""
import os
import uvicorn
from fastapi_server import app

if __name__ == "__main__":
    print("Starting OSINT Microagent FastAPI server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")