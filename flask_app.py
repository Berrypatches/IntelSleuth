"""
OSINT Microagent - Flask Redirect Application
This application runs on port 5000 and redirects to the FastAPI app on port 8000
"""
import os
from flask import Flask, redirect, request, render_template, abort

# Create the Flask application
app = Flask(__name__)

# Mount static files
app.static_folder = 'static'
app.template_folder = 'templates'

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """
    Catch-all route that redirects all requests to the FastAPI server on port 8000
    or serves the index page directly
    """
    # Directly serve the main page rather than redirecting
    if path == '' and request.query_string == b'':
        try:
            return render_template('index.html')
        except Exception as e:
            # If we can't find the template, proxy to FastAPI
            app.logger.error(f"Error rendering template: {e}")
            pass
    
    # Get host without port
    host = request.host.split(':')[0]
    
    # Determine the protocol (http or https)
    protocol = 'https' if request.headers.get('X-Forwarded-Proto') == 'https' else 'http'
    
    # Construct target URL with the same protocol as the original request
    target_url = f"{protocol}://{host}:8000/{path}"
    
    # Include query string if present
    if request.query_string:
        target_url += f"?{request.query_string.decode('utf-8')}"
    
    return redirect(target_url)

@app.errorhandler(400)
def handle_bad_request(e):
    """Handle 400 errors explicitly"""
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors explicitly"""
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)