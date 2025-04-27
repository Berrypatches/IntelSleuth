"""
OSINT Microagent - Redirect Server
Redirects traffic from port 5000 to the main app on port 8000.
"""
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import uvicorn

# Create a FastAPI app
app = FastAPI(title="OSINT Redirect")

@app.get("/{full_path:path}")
async def redirect_to_main_app(request: Request, full_path: str = ""):
    """
    Redirects all traffic from port 5000 to the main app on port 8000
    """
    # Construct the redirect URL
    target_url = f"http://{request.headers.get('host', 'localhost').split(':')[0]}:8000/{full_path}"
    
    # Add query parameters if present
    if request.query_params:
        query_string = request.url.query
        target_url += f"?{query_string}"
    
    return RedirectResponse(url=target_url)

if __name__ == "__main__":
    print("Starting redirect server on port 5000...")
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=True)