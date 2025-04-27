import os
from flask import Flask, redirect, request

# Create a Flask app for forwarding requests
app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # Get the domain from request
    host = request.headers.get('Host', 'localhost:5000')
    domain = host.split(':')[0]
    
    # Forward to the same path on port 8000
    return redirect(f"http://{domain}:8000/{path}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)