from flask import Flask, redirect, request

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # Get the domain from request
    host = request.headers.get('Host', 'localhost:5000')
    domain = host.split(':')[0]
    
    # Forward to the same path on port 8000
    return redirect(f"http://{domain}:8000/{path}")