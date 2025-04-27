from app import create_app
import uvicorn

# Create FastAPI app instance
app = create_app()

# For Gunicorn compatibility, use Uvicorn's WSGI adapter
from uvicorn.middleware.wsgi import WSGIMiddleware

# Wrap the FastAPI app with WSGIMiddleware to make it compatible with WSGI servers
wsgi_app = WSGIMiddleware(app)

# For direct execution
if __name__ == "__main__":
    uvicorn.run("wsgi:app", host="0.0.0.0", port=5000, reload=True)