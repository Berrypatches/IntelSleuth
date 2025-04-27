"""
OSINT Microagent - FastAPI Server Runner
This script starts the FastAPI server on port 8000.
"""
import uvicorn
from app import create_app

if __name__ == "__main__":
    # Create the FastAPI application
    app = create_app()
    
    # Run the FastAPI application
    print("Starting OSINT Microagent FastAPI server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)