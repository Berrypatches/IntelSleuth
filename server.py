"""
OSINT Microagent - Main Server
"""
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from app import create_app

# Create the main FastAPI application
app = create_app()

# Create a separate FastAPI application for port 5000 redirection
redirect_app = FastAPI(title="OSINT Microagent Redirector")

@redirect_app.get("/{full_path:path}")
async def redirect_to_main_app(request: Request, full_path: str = ""):
    """
    Redirects all traffic from port 5000 to the main app on port 8000
    """
    # Get the domain from request
    host = request.headers.get('host', 'localhost:5000')
    domain = host.split(':')[0]
    
    # Forward to the same path on port 8000
    return RedirectResponse(url=f"http://{domain}:8000/{full_path}")

if __name__ == "__main__":
    # Get which app to run based on environment variable
    app_name = os.environ.get("APP_TO_RUN", "main")
    
    if app_name == "redirect":
        # Run the redirector app on port 5000
        print("Starting redirector app on port 5000")
        uvicorn.run(redirect_app, host="0.0.0.0", port=5000)
    else:
        # Run the main app on port 8000
        print("Starting main OSINT app on port 8000")
        uvicorn.run(app, host="0.0.0.0", port=8000)