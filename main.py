import os
import uvicorn
from app import create_app
from flask import Flask, redirect, request

# Create FastAPI app for port 8000
app = create_app()

# Create Flask app for gunicorn compatibility on port 5000
flask_app = Flask(__name__)

@flask_app.route('/', defaults={'path': ''})
@flask_app.route('/<path:path>')
def catch_all(path):
    # Get the domain from request
    host = request.headers.get('Host', 'localhost:5000')
    domain = host.split(':')[0]
    
    # Forward to the same path on port 8000
    return redirect(f"http://{domain}:8000/{path}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
