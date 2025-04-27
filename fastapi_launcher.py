import uvicorn
from app import create_app

# This is the main entry point for the FastAPI application
# It will run on port 8000 and handle all the OSINT functionality

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    # Run the FastAPI application with uvicorn
    uvicorn.run("fastapi_launcher:app", host="0.0.0.0", port=8000, reload=True)