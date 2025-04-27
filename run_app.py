"""
OSINT Microagent - Server Entry Point
Run the FastAPI application directly with Uvicorn.
"""
import uvicorn

if __name__ == "__main__":
    print("Starting OSINT Microagent on port 8000...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)